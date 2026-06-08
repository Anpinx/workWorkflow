#!/usr/bin/env python3
"""Convert PDF to Markdown using automatic local/cloud layout extraction."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Tools.layout_extractor import analyze_document, log_warnings
from Tools.markdown_utils import build_frontmatter, ensure_output_dir, load_dotenv_if_present


def convert(input_path: Path, output_dir: Path, verbose: bool = False) -> Path:
    input_path = Path(input_path)
    basename = input_path.stem
    out_dir = ensure_output_dir(output_dir, basename)
    assets_dir = out_dir / f"{basename}_assets"

    load_dotenv_if_present()
    result = analyze_document(input_path, assets_dir)

    md_path = out_dir / f"{basename}.md"
    frontmatter = build_frontmatter(
        title=basename,
        source=str(input_path),
        converter="pdf_to_md",
        extra={"layout_backend": result.backend},
    )
    md_path.write_text(frontmatter + result.markdown, encoding="utf-8")

    if verbose or result.warnings:
        log_warnings(result.warnings, verbose=True)

    return md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="PDF to Markdown")
    parser.add_argument("--input", "-i", required=True, help="Input PDF path")
    parser.add_argument("--output", "-o", default="output", help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    try:
        out = convert(Path(args.input), Path(args.output), args.verbose)
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
