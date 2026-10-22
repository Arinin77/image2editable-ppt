# Install and use / 安装与使用

## Requirements

- An agent host that can load a `SKILL.md` directory and view the supplied image.
- A PPTX authoring tool or library, plus an available presentation renderer.
- Web access when new website assets are required.
- Python 3 only if using the optional inspection helper; it has no third-party dependencies.

The skill does not install a renderer, fonts or an authoring library. It uses the host's available tools and follows that environment's requirements. Microsoft PowerPoint is one supported rendering path; other compatible renderers need their own output checks.

## Install in Codex

Download and extract this repository, then choose **one** method. Copy the entire skill folder, including `references/`, `scripts/` and `agents/`.

### Ask Codex

Point Codex at the downloaded repository and ask:

> Install the local skill at `skills/image-to-editable-pptx`. Preserve any existing version until I choose to replace it. Then confirm that `image-to-editable-pptx` is discoverable.

After this repository has a public GitHub URL, Codex's `$skill-installer` can also be given the URL of its `skills/image-to-editable-pptx` directory.

### Copy manually

Current Codex documentation lists `~/.agents/skills/` for personal skills and `.agents/skills/` in a repository for project skills. From the extracted repository root:

Windows PowerShell:

```powershell
$skillRoot = Join-Path $HOME '.agents\skills'
$skillTarget = Join-Path $skillRoot 'image-to-editable-pptx'
if (Test-Path -LiteralPath $skillTarget) { throw 'Skill already exists; review it before replacing.' }
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
Copy-Item -LiteralPath '.\skills\image-to-editable-pptx' -Destination $skillRoot -Recurse
```

macOS / Linux shell:

```sh
skill_root="$HOME/.agents/skills"
skill_target="$skill_root/image-to-editable-pptx"
if [ -e "$skill_target" ]; then
  echo 'Skill already exists; review it before replacing.' >&2
else
  mkdir -p "$skill_root" && cp -R ./skills/image-to-editable-pptx "$skill_root/"
fi
```

If your existing installation is already discovered from another configured directory, update that copy rather than creating duplicate skills with the same name. Newly installed skills should be discovered automatically; restart Codex if the skill does not appear. [Official skill locations and discovery](https://learn.chatgpt.com/docs/build-skills).

## First conversion

Attach a complete, readable source image. In Codex, explicitly mention `$image-to-editable-pptx`, or select the skill in the host's skill picker. Example:

> Rebuild this image as an editable PPTX. Keep its text, layout and arrow meanings. Preserve suitable original icons; use website replacements only where needed. Save the new PPTX separately from the input.

Add a style reference or preferred icon source when you have one. If the source is incomplete or a choice would change its meaning, the skill asks a focused question. It does not require a questionnaire for a clear source.

Open the result in your target presentation application. Check a text label, a shape, an arrow and an independent icon. Pictures are replaceable objects, not necessarily editable vector strokes.

## 中文速查

1. 下载仓库，复制完整的 `skills/image-to-editable-pptx` 文件夹，不能只复制 `SKILL.md`。
2. 可让 Codex 安装；手动安装时选一个技能目录即可。已有同名技能先核对，避免重复安装。
3. 附上清晰完整的图片，输入“请用 `$image-to-editable-pptx` 重建为可编辑 PPT”，可补充风格参考与图标来源偏好。
4. 宿主需要图片查看、PPTX 构建和渲染工具；技能本身不会自动安装这些环境。
5. 打开导出的 PPTX 检查文字、形状、箭头和图标。可选检查脚本需要 Python 3 标准库，不需要额外 Python 包。

This repository distributes the standalone skill. Marketplace submission or plugin installation is not required to inspect these examples or load the skill locally.
