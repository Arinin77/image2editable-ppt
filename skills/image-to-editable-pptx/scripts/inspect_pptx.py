#!/usr/bin/env python3
"""Inventory current-slide OOXML objects; this is not an editability or visual verdict."""
import argparse
import json
import posixpath
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree as ET


class InventoryError(Exception):
    pass


def local(tag):
    return tag.rsplit("}", 1)[-1]


def child(element, name):
    return next((e for e in element if local(e.tag) == name), None) if element is not None else None


def xml(package, part):
    try:
        return ET.fromstring(package.read(part))
    except KeyError as exc:
        raise InventoryError("Required package part is missing: " + part) from exc
    except ET.ParseError as exc:
        raise InventoryError("Invalid XML in " + part + ": " + str(exc)) from exc


def target_part(owner, target):
    if not target:
        raise InventoryError("Empty relationship target in " + (owner or "package root"))
    target = unquote(target)
    part = posixpath.normpath(target.lstrip("/") if target.startswith("/")
                             else posixpath.join(posixpath.dirname(owner), target))
    if part.startswith("../") or part in ("..", "."):
        raise InventoryError("Relationship target escapes the package: " + target)
    return part


def relationships(package, owner, required=False):
    part = posixpath.join(posixpath.dirname(owner), "_rels", posixpath.basename(owner)+".rels") if owner else "_rels/.rels"
    if not required and part not in package.namelist():
        return {}
    root = xml(package, part)
    if local(root.tag) != "Relationships":
        raise InventoryError("Expected Relationships XML in " + part)
    return {e.get("Id"): {"type": e.get("Type", "").rsplit("/", 1)[-1],
                           "external": e.get("TargetMode") == "External",
                           "target": e.get("Target")}
            for e in root if local(e.tag) == "Relationship"}


def text_content(element):
    if element is None:
        return ""
    paragraphs = []
    for p in element.iter():
        if local(p.tag) == "p":
            paragraphs.append("".join((e.text or "") if local(e.tag) == "t"
                                      else "\n" if local(e.tag) == "br" else "\t"
                                      for e in p.iter() if local(e.tag) in ("t", "br", "tab")))
    return "\n".join(paragraphs)


def blips(element, rels, owner, package):
    result = []
    if element is not None:
        for node in element.iter():
            if local(node.tag) not in ("blip", "svgBlip"):
                continue
            references = [(local(k), v) for k, v in node.attrib.items() if local(k) in ("embed", "link")]
            for reference, rid in references or [(None, None)]:
                rel = rels.get(rid)
                row = {"element": local(node.tag), "reference": reference, "relationship_id": rid,
                       "relationship_status": "resolved" if rel else "missing",
                       "target_status": "unresolved"}
                if rel:
                    row["target"] = rel["target"] if rel["external"] else target_part(owner, rel["target"])
                    row["external"] = rel["external"]
                    row["target_status"] = ("external" if rel["external"] else
                                            "present" if row["target"] in package.namelist() else "missing")
                result.append(row)
    return result


def inspect_slide(package, part, index):
    root = xml(package, part)
    if local(root.tag) != "sld":
        raise InventoryError("Expected a slide XML root in " + part)
    rels = relationships(package, part)
    counts = dict.fromkeys(("native_text_shapes", "native_shapes", "custom_path_shapes", "custom_paths",
                           "connectors", "pictures", "groups", "tables", "charts", "other_graphic_frames"), 0)
    objects, texts, picture_fills, review = [], [], [], []

    def walk(container, group_path=()):
        for node in container:
            kind = local(node.tag)
            if kind in ("nvGrpSpPr", "grpSpPr", "extLst"):
                continue
            if kind not in ("sp", "cxnSp", "pic", "grpSp", "graphicFrame"):
                review.append({"kind": "unsupported_shape_tree_node", "node": kind,
                               "note": "Not expanded or counted; inspect manually."})
                continue
            nv = next((e for e in node.iter() if local(e.tag) == "cNvPr"), None)
            row = {"type": kind, "id": nv.get("id") if nv is not None else None,
                   "name": nv.get("name") if nv is not None else None,
                   "group_path": list(group_path)}
            if nv is not None and nv.get("descr"):
                row["description"] = nv.get("descr")
            objects.append(row)
            if kind == "grpSp":
                counts["groups"] += 1
                walk(node, group_path+(row["name"] or row["id"] or "(unnamed group)",))
                continue
            if kind in ("sp", "cxnSp"):
                counts["native_shapes" if kind == "sp" else "connectors"] += 1
                if kind == "cxnSp":
                    connection_properties = child(child(node, "nvCxnSpPr"), "cNvCxnSpPr")
                    row["attachments"] = {}
                    for endpoint, tag in (("start", "stCxn"), ("end", "endCxn")):
                        connection = child(connection_properties, tag)
                        row["attachments"][endpoint] = None if connection is None else {
                            "target_id": connection.get("id"), "site_index": connection.get("idx")}
                body = child(node, "txBody")
                content = text_content(body)
                if content.strip():
                    counts["native_text_shapes"] += int(kind == "sp")
                    texts.append({"object_id": row["id"], "name": row["name"], "type": kind, "text": content})
                sppr = child(node, "spPr")
                geometry = child(sppr, "custGeom")
                paths = child(geometry, "pathLst")
                if geometry is not None:
                    row["geometry"] = "custom"
                    row["custom_paths"] = sum(local(p.tag) == "path" for p in paths) if paths is not None else 0
                    row["path_commands"] = sorted({local(e.tag) for e in geometry.iter()
                                                   if local(e.tag) in ("moveTo", "lnTo", "arcTo", "quadBezTo", "cubicBezTo", "close")})
                    counts["custom_path_shapes"] += 1
                    counts["custom_paths"] += row["custom_paths"]
                else:
                    preset = child(sppr, "prstGeom")
                    row["geometry"] = preset.get("prst") if preset is not None else "unknown"
                fill = child(sppr, "blipFill")
                if fill is not None:
                    picture_fills.append({"object_id": row["id"], "name": row["name"], "blips": blips(fill, rels, part, package)})
            elif kind == "pic":
                counts["pictures"] += 1
                row["blips"] = blips(child(node, "blipFill"), rels, part, package)
            elif kind == "graphicFrame":
                graphic = child(node, "graphic")
                data = child(graphic, "graphicData")
                contains = {local(e.tag) for e in data.iter()} if data is not None else set()
                row["content_types"] = [name for name in ("tbl", "chart") if name in contains]
                counts["tables"] += int("tbl" in contains)
                counts["charts"] += int("chart" in contains)
                counts["other_graphic_frames"] += int(not row["content_types"])
                if "tbl" in contains:
                    texts.append({"object_id": row["id"], "name": row["name"], "type": "table", "text": text_content(data)})

    csld = child(root, "cSld")
    tree = child(csld, "spTree")
    if tree is None:
        raise InventoryError("Required slide shape tree is missing: " + part)
    walk(tree)
    objects_by_id = {}
    for row in objects:
        objects_by_id.setdefault(row["id"], []).append(row)
    for object_id, matches in objects_by_id.items():
        if object_id is not None and len(matches) > 1:
            review.append({"kind": "duplicate_object_id", "object_id": object_id,
                           "names": [row["name"] for row in matches]})
    attachment_counts = {"both_ends": 0, "one_end": 0, "neither_end": 0, "invalid_endpoints": 0}
    for row in objects:
        if row["type"] != "cxnSp":
            continue
        declared = sum(value is not None for value in row["attachments"].values())
        attachment_counts[("neither_end", "one_end", "both_ends")[declared]] += 1
        for endpoint, value in row["attachments"].items():
            if value is None:
                continue
            matches = objects_by_id.get(value["target_id"], [])
            value["target_status"] = "present" if len(matches) == 1 else "missing" if not matches else "ambiguous"
            if len(matches) == 1:
                value["target_name"] = matches[0]["name"]
            site = value["site_index"]
            valid_site = isinstance(site, str) and site.isdecimal()
            if len(matches) != 1 or not valid_site:
                attachment_counts["invalid_endpoints"] += 1
                review.append({"kind": "invalid_connector_attachment", "name": row["name"],
                               "endpoint": endpoint, **value,
                               "note": "Check target ID and nonnegative site index. Site geometry and movement are not tested."})
    background = blips(child(child(csld, "bg"), "bgPr"), rels, part, package)
    if background:
        review.append({"kind": "background_blip", "note": "Inspect background image content manually."})
    if picture_fills:
        review.append({"kind": "shape_picture_fill", "note": "An otherwise native shape may contain bitmap-filled content."})
    if counts["pictures"] and not counts["native_text_shapes"]:
        review.append({"kind": "pictures_without_native_text_shapes", "note": "Inspect whether page content is flattened; an image-only page may also be intentional."})
    inherited = []
    for rid, rel in rels.items():
        if rel["type"] not in ("slideLayout", "slideMaster"):
            continue
        layer = {"relationship_id": rid, "type": rel["type"], "target": rel["target"], "external": rel["external"]}
        if not rel["external"]:
            layer["part"] = target_part(part, rel["target"])
        inherited.append(layer)
    if inherited:
        review.append({"kind": "layout_master_inheritance", "note": "Layout/master contents and their inherited backgrounds are not expanded into these counts; inspect them manually."})
    assets = [("background", None, background)]
    assets += [("picture", row["name"], row["blips"]) for row in objects if "blips" in row]
    assets += [("shape_picture_fill", row["name"], row["blips"]) for row in picture_fills]
    for source, name, references in assets:
        for asset in references:
            flag = {"missing": "missing_asset_target", "unresolved": "unresolved_asset_relationship",
                    "external": "external_asset"}.get(asset["target_status"])
            if flag:
                review.append({"kind": flag, "source": source, "name": name,
                               "relationship_id": asset["relationship_id"], "target": asset.get("target"),
                               "note": "External assets are not fetched." if flag == "external_asset" else
                                       "Repair the missing relationship or package target before delivery."})
    return {"slide": index, "part": part, "counts": counts, "connector_attachments": attachment_counts, "objects": objects, "texts": texts,
            "picture_fills": picture_fills, "background_blips": background,
            "inheritance_relationships": inherited, "manual_review": review}


def inspect_pptx(file):
    with zipfile.ZipFile(file) as package:
        xml(package, "[Content_Types].xml")
        root_rels = relationships(package, "", required=True)
        office = next((r for r in root_rels.values() if r["type"] == "officeDocument" and not r["external"]), None)
        if office is None:
            raise InventoryError("No internal officeDocument relationship in _rels/.rels")
        main = target_part("", office["target"])
        presentation = xml(package, main)
        if local(presentation.tag) != "presentation":
            raise InventoryError("Expected presentation XML root in " + main)
        rels = relationships(package, main, required=True)
        slide_list = child(presentation, "sldIdLst")
        if slide_list is None:
            raise InventoryError("Required slide relationship order is missing in " + main)
        slides = []
        for sid in slide_list:
            if local(sid.tag) != "sldId":
                continue
            rid = next((v for k, v in sid.attrib.items() if k.startswith("{") and local(k) == "id"), None)
            rel = rels.get(rid)
            if rel is None or rel["external"] or rel["type"] != "slide":
                raise InventoryError("Unresolved internal slide relationship: " + str(rid))
            slides.append(inspect_slide(package, target_part(main, rel["target"]), len(slides)+1))
    return {"schema_version": 3, "input": str(Path(file).resolve()), "evidence_type": "ooxml_inventory_only",
            "not_verified": ["visual quality", "semantic correctness", "editability in a target application", "asset provenance and licenses"],
            "counting_notes": ["native_shapes counts p:sp, including text shapes; connectors count p:cxnSp separately.",
                               "Custom freeform arrows/curves may be native shapes rather than connectors.",
                               "Nested group contents are included. Table text is recorded separately from native text shapes.",
                               "Texts follow presentation slide order, then depth-first shape-tree order; this is not spatial reading order.",
                               "Asset target presence checks ZIP entries only; image decoding and external URLs are not checked.",
                               "Embedded chart data/text and layout/master contents are not inventoried."],
            "slides": slides}


def verify_text(report, expected):
    """Compare named text objects without changing case, punctuation, or non-whitespace characters."""
    if not isinstance(expected, dict) or set(expected) != {"slides"} or not isinstance(expected["slides"], list):
        raise InventoryError('--expect-text requires {"slides": [{"slide": 1, "texts": [{"name": "title", "text": "Exact text"}]}]}')
    results, seen = [], set()
    slides = {slide["slide"]: slide for slide in report["slides"]}
    for page in expected["slides"]:
        if (not isinstance(page, dict) or set(page) != {"slide", "texts"} or
                type(page["slide"]) is not int or page["slide"] < 1 or not isinstance(page["texts"], list)):
            raise InventoryError("Each expected slide needs a positive integer slide and a texts list.")
        for item in page["texts"]:
            if (not isinstance(item, dict) or set(item) != {"name", "text"} or
                    not isinstance(item["name"], str) or not item["name"] or not isinstance(item["text"], str)):
                raise InventoryError("Each expected text needs a nonempty object name and a text string.")
            key = (page["slide"], item["name"])
            if key in seen:
                raise InventoryError("Duplicate expected slide/name: " + str(key))
            seen.add(key)
            row = {"slide": page["slide"], "name": item["name"], "expected": item["text"]}
            slide = slides.get(page["slide"])
            matches = [obj for obj in slide["objects"] if obj["name"] == item["name"]] if slide else []
            if slide is None:
                row["status"] = "missing_slide"
            elif not matches:
                row["status"] = "missing_object"
            elif len(matches) != 1:
                row["status"] = "ambiguous_object_name"
            else:
                row["actual"] = next((obj["text"] for obj in slide["texts"]
                                      if obj["object_id"] == matches[0]["id"]), "")
                row["status"] = "matched" if "".join(row["actual"].split()) == "".join(item["text"].split()) else "mismatch"
            results.append(row)
    report["text_verification"] = {"whitespace_policy": "Ignore whitespace only; all other characters must match exactly.",
                                   "scope": "Only the named expectations are compared; extra objects/text are not rejected.",
                                   "checks": results}


def summarize(report, output=None):
    counts, flags, assets, attachments = {}, {}, {}, {}
    for slide in report["slides"]:
        for kind, count in slide["connector_attachments"].items():
            attachments[kind] = attachments.get(kind, 0) + count
        for kind, count in slide["counts"].items():
            counts[kind] = counts.get(kind, 0) + count
        for flag in slide["manual_review"]:
            flags.setdefault(flag["kind"], []).append(slide["slide"])
        references = list(slide["background_blips"])
        references += [b for row in slide["objects"] for b in row.get("blips", [])]
        references += [b for row in slide["picture_fills"] for b in row["blips"]]
        for asset in references:
            status = asset["target_status"]
            assets[status] = assets.get(status, 0) + 1
    text_checks = report.get("text_verification", {}).get("checks", [])
    for check in text_checks:
        if check["status"] != "matched":
            flags.setdefault("expected_text_" + check["status"], []).append(check["slide"])
    summary = {"schema_version": report["schema_version"], "input": report["input"],
               "evidence_type": report["evidence_type"], "slides": len(report["slides"]),
               "counts": counts, "connector_attachments": attachments, "asset_references": assets,
               "review_flags": [{"kind": kind, "slides": sorted(set(pages)), "occurrences": len(pages)}
                                for kind, pages in sorted(flags.items())],
               "not_verified": report["not_verified"]}
    if "text_verification" in report:
        summary["text_verification"] = {"checked": len(text_checks),
                                        "matched": sum(row["status"] == "matched" for row in text_checks),
                                        "issues": sum(row["status"] != "matched" for row in text_checks)}
    if output:
        summary["full_report"] = str(output.resolve())
    return summary


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, epilog="Exit 0 means inventory generated, not a semantic/visual PASS. Exit 2 means an input or output error.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, help="Save the complete JSON report; stdout remains a compact summary unless --full is set.")
    parser.add_argument("--full", action="store_true", help="Print the full report instead of the default compact summary.")
    parser.add_argument("--expect-text", type=Path, metavar="JSON", help='Compare named text: {"slides":[{"slide":1,"texts":[{"name":"title","text":"Exact text"}]}]}. Slide numbers are 1-based; only whitespace is ignored. Extra text is not rejected.')
    args = parser.parse_args()
    try:
        for protected in (args.input, args.expect_text):
            if args.output and protected and (args.output.resolve() == protected.resolve() or
                    (args.output.exists() and protected.exists() and args.output.samefile(protected))):
                raise InventoryError("--output must not overwrite the input PPTX or expected-text JSON")
        report = inspect_pptx(args.input)
        if args.expect_text:
            verify_text(report, json.loads(args.expect_text.read_text(encoding="utf-8-sig")))
        content = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content+"\n", encoding="utf-8")
        print(content if args.full else json.dumps(summarize(report, args.output), ensure_ascii=False, indent=2))
        return 0
    except (InventoryError, OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"error": str(exc), "evidence_type": "ooxml_inventory_only"}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
