#!/usr/bin/env python3
"""Convert Markdown to Word (.docx) using template styles."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Tools.docx_builder import build_docx, create_default_template
from Tools.markdown_utils import load_dotenv_if_present, strip_frontmatter


def convert(
    input_path: Path,
    output_dir: Path,
    template_path: Path | None = None,
) -> Path:
    input_path = Path(input_path)
    load_dotenv_if_present()

    template = template_path or Path(
        os.environ.get("DEFAULT_DOCX_TEMPLATE", ROOT / "template" / "default.docx")
    )
    if not template.exists():
        create_default_template(template)

    text = input_path.read_text(encoding="utf-8")
    _meta, body = strip_frontmatter(text)

    basename = input_path.stem
    out_dir = output_dir / basename
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{basename}.docx"

    build_docx(body, template, out_path)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Markdown to Word")
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", default="output")
    parser.add_argument("--template", "-t", default=None, help="Path to .docx template")
    args = parser.parse_args()

    try:
        tpl = Path(args.template) if args.template else None
        out = convert(Path(args.input), Path(args.output), tpl)
        print(out)
        return 0
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
