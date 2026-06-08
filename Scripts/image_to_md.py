#!/usr/bin/env python3
"""Convert images to Markdown using automatic local/cloud layout extraction."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Tools.layout_extractor import analyze_document, log_warnings
from Tools.markdown_utils import build_frontmatter, ensure_output_dir, load_dotenv_if_present

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}


def convert(input_path: Path, output_dir: Path, verbose: bool = False) -> Path:
    input_path = Path(input_path)
    if input_path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError(f"Unsupported image format: {input_path.suffix}")

    basename = input_path.stem
    out_dir = ensure_output_dir(output_dir, basename)
    assets_dir = out_dir / f"{basename}_assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    load_dotenv_if_present()
    result = analyze_document(input_path, assets_dir)

    md_path = out_dir / f"{basename}.md"
    frontmatter = build_frontmatter(
        title=basename,
        source=str(input_path),
        converter="image_to_md",
        extra={"layout_backend": result.backend},
    )
    body = result.markdown
    if not body.strip():
        rel = f"{assets_dir.name}/{input_path.name}"
        import shutil

        shutil.copy2(input_path, assets_dir / input_path.name)
        body = f"![{basename}]({rel})\n"

    md_path.write_text(frontmatter + body, encoding="utf-8")

    if verbose or result.warnings:
        log_warnings(result.warnings, verbose=True)

    return md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Image to Markdown")
    parser.add_argument("--input", "-i", required=True, help="Input image path")
    parser.add_argument("--output", "-o", default="output", help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    try:
        out = convert(Path(args.input), Path(args.output), args.verbose)
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
