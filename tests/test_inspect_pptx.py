"""Small synthetic package checks; no model or visual-quality benchmark."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/image-to-editable-pptx/scripts/inspect_pptx.py"
SPEC = importlib.util.spec_from_file_location("inspect_pptx", SCRIPT)
inspector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inspector)
NS = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'


def rels(entries):
    return '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(
        f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/{kind}" Target="{target}"' +
        (' TargetMode="External"' if external else '') + '/>'
        for rid, kind, target, external in entries) + '</Relationships>'


def shape(number, name, text="", fill=""):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{number}" name="{name}"/></p:nvSpPr>'
            f'<p:spPr><a:prstGeom prst="rect"/>{fill}</p:spPr>'
            f'<p:txBody><a:p><a:r><a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp>')


def picture(number, name, reference):
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{number}" name="{name}"/></p:nvPicPr>'
            f'<p:blipFill><a:blip {reference}/></p:blipFill></p:pic>')


def slide(body, background=""):
    return f'<p:sld {NS}><p:cSld>{background}<p:spTree>{body}</p:spTree></p:cSld></p:sld>'


def connector(number, start=None, end=None):
    endpoints = ''.join(f'<a:{tag} id="{target}" idx="{site}"/>'
                        for tag, value in (("stCxn", start), ("endCxn", end)) if value
                        for target, site in (value,))
    return (f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{number}" name="edge-{number}"/>'
            f'<p:cNvCxnSpPr>{endpoints}</p:cNvCxnSpPr></p:nvCxnSpPr>'
            '<p:spPr><a:prstGeom prst="line"/></p:spPr></p:cxnSp>')


def make_package(path, pages, page_rels=None, media=None):
    """pages preserve supplied presentation order, independently of part filenames."""
    page_rels, media = page_rels or {}, media or {}
    with zipfile.ZipFile(path, "w") as package:
        package.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        package.writestr("_rels/.rels", rels([("root", "officeDocument", "ppt/presentation.xml", False)]))
        package.writestr("ppt/presentation.xml", f'<p:presentation {NS}><p:sldIdLst>' + ''.join(
            f'<p:sldId id="{index+256}" r:id="slide{index}"/>' for index in range(len(pages))) + '</p:sldIdLst></p:presentation>')
        package.writestr("ppt/_rels/presentation.xml.rels", rels([
            (f"slide{index}", "slide", f"slides/{name}", False) for index, (name, _) in enumerate(pages)]))
        for name, content in pages:
            package.writestr("ppt/slides/" + name, content)
            if name in page_rels:
                package.writestr("ppt/slides/_rels/" + name + ".rels", rels(page_rels[name]))
        for name, content in media.items():
            package.writestr(name, content)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pptx = self.root / "fixture.pptx"
        make_package(self.pptx, [("slide1.xml", slide(shape(1, "title", "Knowledge Coverage")))])

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), str(self.pptx), *map(str, args)],
                              capture_output=True, text=True, encoding="utf-8", check=False)

    def test_nested_groups_and_presentation_shape_tree_order(self):
        group = '<p:grpSp><p:nvGrpSpPr><p:cNvPr id="9" name="outer"/></p:nvGrpSpPr><p:grpSp>'
        group += '<p:nvGrpSpPr><p:cNvPr id="10" name="inner"/></p:nvGrpSpPr>' + shape(2, "inside", "Second") + '</p:grpSp></p:grpSp>'
        make_package(self.pptx, [("slide10.xml", slide(shape(1, "start", "First") + group + shape(3, "end", "Third"))),
                                 ("slide2.xml", slide(shape(4, "next", "Last")))])
        report = inspector.inspect_pptx(self.pptx)
        self.assertEqual([page["part"] for page in report["slides"]], ["ppt/slides/slide10.xml", "ppt/slides/slide2.xml"])
        self.assertEqual([item["text"] for item in report["slides"][0]["texts"]], ["First", "Second", "Third"])
        self.assertEqual(report["slides"][0]["counts"]["groups"], 2)
        inside = next(obj for obj in report["slides"][0]["objects"] if obj["name"] == "inside")
        self.assertEqual(inside["group_path"], ["outer", "inner"])

    def test_missing_media_in_picture_fill_and_background_and_external(self):
        fill = '<a:blipFill><a:blip r:embed="lost"/></a:blipFill>'
        background = '<p:bg><p:bgPr>' + fill + '</p:bgPr></p:bg>'
        body = shape(1, "filled", "Text", fill) + picture(2, "missing", 'r:embed="lost"')
        body += picture(3, "unknown", 'r:embed="unknown"') + picture(4, "dual", 'r:embed="ok" r:link="remote"')
        make_package(self.pptx, [("slide1.xml", slide(body, background))], {"slide1.xml": [
            ("lost", "image", "../media/missing.png", False), ("ok", "image", "../media/image%201.png", False),
            ("remote", "image", "https://example.com/image.png", True)]}, {"ppt/media/image 1.png": b"fixture"})
        report = inspector.inspect_pptx(self.pptx)
        summary = inspector.summarize(report)
        self.assertEqual(summary["asset_references"], {"missing": 3, "unresolved": 1, "present": 1, "external": 1})
        issues = {flag["kind"]: flag for flag in summary["review_flags"]}
        self.assertEqual(issues["missing_asset_target"]["occurrences"], 3)
        self.assertEqual(issues["missing_asset_target"]["slides"], [1])
        self.assertIn("external_asset", issues)
        self.assertIn("unresolved_asset_relationship", issues)

    def test_review_flags_deduplicate_slides(self):
        make_package(self.pptx, [("slide1.xml", slide(shape(1, "a", "a"))), ("slide2.xml", slide(shape(2, "b", "b")))],
                     {name: [("layout", "slideLayout", "../slideLayouts/layout.xml", False)] for name in ("slide1.xml", "slide2.xml")})
        summary = inspector.summarize(inspector.inspect_pptx(self.pptx))
        self.assertEqual(summary["review_flags"], [{"kind": "layout_master_inheritance", "slides": [1, 2], "occurrences": 2}])

    def test_svg_extension_target_checked_with_present_png_fallback(self):
        body = ('<p:pic><p:nvPicPr><p:cNvPr id="1" name="svg-icon"/></p:nvPicPr>'
                '<p:blipFill><a:blip r:embed="png"><a:extLst><a:ext uri="svg">'
                '<asvg:svgBlip xmlns:asvg="http://schemas.microsoft.com/office/drawing/2016/SVG/main" '
                'r:embed="svg"/></a:ext></a:extLst></a:blip></p:blipFill></p:pic>')
        make_package(self.pptx, [("slide1.xml", slide(body))], {"slide1.xml": [
            ("png", "image", "../media/fallback.png", False), ("svg", "image", "../media/missing.svg", False)]},
            {"ppt/media/fallback.png": b"fixture"})
        report = inspector.inspect_pptx(self.pptx)
        references = report["slides"][0]["objects"][0]["blips"]
        self.assertEqual([(row["element"], row["target_status"]) for row in references],
                         [("blip", "present"), ("svgBlip", "missing")])
        summary = inspector.summarize(report)
        self.assertEqual(summary["asset_references"], {"present": 1, "missing": 1})
        missing = next(flag for flag in summary["review_flags"] if flag["kind"] == "missing_asset_target")
        self.assertEqual(missing, {"kind": "missing_asset_target", "slides": [1], "occurrences": 1})

    def test_default_summary_output_keeps_full_evidence_and_full_opt_in(self):
        report_path = self.root / "reports/full.json"
        result = self.run_cli("--output", report_path)
        self.assertEqual(result.returncode, 0, result.stderr)
        summary, full = json.loads(result.stdout), json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(summary["slides"], 1)
        self.assertNotIn("objects", summary)
        self.assertEqual(full["slides"][0]["texts"][0]["text"], "Knowledge Coverage")
        self.assertEqual(summary["full_report"], str(report_path.resolve()))
        result = self.run_cli("--full")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), full)

    def test_text_whitespace_only_matching_and_mismatch(self):
        expected = self.root / "expected.json"
        expected.write_text(json.dumps({"slides": [{"slide": 1, "texts": [{"name": "title", "text": "Knowledge\nCoverage"}]}]}), encoding="utf-8")
        result = self.run_cli("--expect-text", expected)
        self.assertEqual(json.loads(result.stdout)["text_verification"], {"checked": 1, "matched": 1, "issues": 0})
        expected.write_text(json.dumps({"slides": [{"slide": 1, "texts": [{"name": "title", "text": "Knowledge coverage"}]}]}), encoding="utf-8")
        result = self.run_cli("--expect-text", expected, "--full")
        self.assertEqual(result.returncode, 0, result.stderr)
        check = json.loads(result.stdout)["text_verification"]["checks"][0]
        self.assertEqual(check["status"], "mismatch")
        self.assertEqual(check["actual"], "Knowledge Coverage")

    def test_missing_or_ambiguous_expected_objects(self):
        make_package(self.pptx, [("slide1.xml", slide(shape(1, "same", "One") + shape(2, "same", "Two")))])
        report = inspector.inspect_pptx(self.pptx)
        inspector.verify_text(report, {"slides": [{"slide": 1, "texts": [{"name": "same", "text": "One"}, {"name": "absent", "text": "X"}]},
                                                  {"slide": 2, "texts": [{"name": "absent", "text": "X"}]}]})
        self.assertEqual([item["status"] for item in report["text_verification"]["checks"]],
                         ["ambiguous_object_name", "missing_object", "missing_slide"])

    def test_invalid_expected_schema(self):
        report = inspector.inspect_pptx(self.pptx)
        for expected in ({"slides": [{"slide": True, "texts": []}]}, {"slides": [{"slide": 1, "texts": [{"name": "x", "text": "x"}] * 2}]}, []):
            with self.subTest(expected=expected), self.assertRaises(inspector.InventoryError):
                inspector.verify_text(report, expected)

    def test_output_cannot_overwrite_inputs(self):
        original = self.pptx.read_bytes()
        result = self.run_cli("--output", self.pptx)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.pptx.read_bytes(), original)
        expected = self.root / "expected.json"
        expected.write_text('{"slides": []}', encoding="utf-8")
        result = self.run_cli("--expect-text", expected, "--output", expected)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(expected.read_text(encoding="utf-8"), '{"slides": []}')

    def test_bad_zip_reports_error_without_traceback(self):
        self.pptx.write_bytes(b"not a zip")
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("error", json.loads(result.stderr))
        self.assertEqual(result.stdout, "")

    def test_connector_attachment_counts_and_target_names(self):
        body = shape(1, "start", "Start") + shape(2, "finish", "Finish")
        body += connector(3, (1, 3), (2, 1)) + connector(4, (1, 3)) + connector(5)
        make_package(self.pptx, [("slide1.xml", slide(body))])
        report = inspector.inspect_pptx(self.pptx)
        self.assertEqual(inspector.summarize(report)["connector_attachments"],
                         {"both_ends": 1, "one_end": 1, "neither_end": 1, "invalid_endpoints": 0})
        edge = next(x for x in report["slides"][0]["objects"] if x["id"] == "3")
        self.assertEqual(edge["attachments"]["end"]["target_name"], "finish")
        self.assertFalse(report["slides"][0]["manual_review"])

    def test_dangling_and_malformed_connector_endpoints(self):
        body = shape(1, "start") + connector(2, (99, 0), (1, -1))
        make_package(self.pptx, [("slide1.xml", slide(body))])
        summary = inspector.summarize(inspector.inspect_pptx(self.pptx))
        self.assertEqual(summary["connector_attachments"]["invalid_endpoints"], 2)
        self.assertEqual(summary["review_flags"][0]["kind"], "invalid_connector_attachment")

    def test_connector_can_reference_nested_shape(self):
        group = '<p:grpSp><p:nvGrpSpPr><p:cNvPr id="9" name="module"/></p:nvGrpSpPr>'
        group += shape(1, "nested") + '</p:grpSp>' + shape(2, "outside") + connector(3, (1, 3), (2, 1))
        make_package(self.pptx, [("slide1.xml", slide(group))])
        report = inspector.inspect_pptx(self.pptx)
        self.assertEqual(report["slides"][0]["connector_attachments"]["invalid_endpoints"], 0)

    def test_duplicate_target_id_is_ambiguous(self):
        body = shape(1, "first") + shape(1, "second") + connector(2, (1, 0))
        make_package(self.pptx, [("slide1.xml", slide(body))])
        flags = {x["kind"] for x in inspector.summarize(inspector.inspect_pptx(self.pptx))["review_flags"]}
        self.assertEqual(flags, {"duplicate_object_id", "invalid_connector_attachment"})


if __name__ == "__main__":
    unittest.main()
