#!/usr/bin/env python3
"""Convert Word (.docx) to Markdown via mammoth."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Tools.markdown_utils import build_frontmatter, ensure_output_dir


def convert(input_path: Path, output_dir: Path) -> Path:
    import mammoth
    from markdownify import markdownify as md

    input_path = Path(input_path)
    if input_path.suffix.lower() not in (".docx", ".doc"):
        raise ValueError(f"Expected .docx or .doc, got {input_path.suffix}")

    if input_path.suffix.lower() == ".doc":
        raise ValueError(
            "Legacy .doc format requires LibreOffice pre-conversion to .docx. "
            "Run: soffice --headless --convert-to docx input.doc"
        )

    basename = input_path.stem
    out_dir = ensure_output_dir(output_dir, basename)

    with open(input_path, "rb") as f:
        result = mammoth.convert_to_html(f)

    html = result.value
    markdown = md(html, heading_style="ATX")

    warnings = [str(m) for m in result.messages]
    if warnings:
        markdown += "\n\n<!-- Conversion notes:\n"
        markdown += "\n".join(f"- {w}" for w in warnings)
        markdown += "\n-->\n"

    md_path = out_dir / f"{basename}.md"
    frontmatter = build_frontmatter(
        title=basename,
        source=str(input_path),
        converter="docx_to_md",
    )
    md_path.write_text(frontmatter + markdown, encoding="utf-8")
    return md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Word to Markdown")
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", default="output")
    args = parser.parse_args()

    try:
        out = convert(Path(args.input), Path(args.output))
        print(out)
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
