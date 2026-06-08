#!/usr/bin/env python3
"""Unified CLI for Workflow document conversion pipeline."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Tools.markdown_utils import load_dotenv_if_present

EXTENSION_MAP = {
    ".pdf": "pdf-to-md",
    ".docx": "docx-to-md",
    ".doc": "docx-to-md",
    ".xlsx": "xlsx-to-md",
    ".xls": "xlsx-to-md",
    ".pptx": "pptx-to-md",
    ".ppt": "pptx-to-md",
    ".png": "image-to-md",
    ".jpg": "image-to-md",
    ".jpeg": "image-to-md",
    ".tiff": "image-to-md",
    ".tif": "image-to-md",
    ".bmp": "image-to-md",
    ".webp": "image-to-md",
    ".md": "md-to-docx",
    ".json": "chart-to-drawio",
    ".mmd": "chart-to-drawio",
    ".mermaid": "chart-to-drawio",
}

SCRIPT_MAP = {
    "pdf-to-md": "pdf_to_md.py",
    "docx-to-md": "docx_to_md.py",
    "md-to-docx": "md_to_docx.py",
    "xlsx-to-md": "xlsx_to_md.py",
    "pptx-to-md": "pptx_to_md.py",
    "image-to-md": "image_to_md.py",
    "chart-to-drawio": "chart_to_drawio.py",
}


def _run_script(script: str, args: list[str]) -> int:
    script_path = ROOT / "Scripts" / script
    cmd = [sys.executable, str(script_path)] + args
    result = subprocess.run(cmd, cwd=str(ROOT))
    return result.returncode


def detect_task(input_path: Path) -> str:
    ext = input_path.suffix.lower()
    if ext not in EXTENSION_MAP:
        raise ValueError(
            f"Unsupported extension '{ext}'. Supported: {', '.join(sorted(set(EXTENSION_MAP)))}"
        )
    return EXTENSION_MAP[ext]


def run_task(
    task: str,
    input_path: Path,
    output_dir: Path,
    template: str | None = None,
    verbose: bool = False,
) -> int:
    if task not in SCRIPT_MAP:
        print(f"ERROR: Unknown task '{task}'", file=sys.stderr)
        return 1

    script = SCRIPT_MAP[task]
    args = ["--input", str(input_path), "--output", str(output_dir)]
    if verbose:
        args.append("--verbose")
    if task == "md-to-docx" and template:
        args.extend(["--template", template])
    if task == "chart-to-drawio":
        if str(output_dir).lower().endswith(".drawio"):
            out_file = output_dir
        else:
            out_file = output_dir / f"{input_path.stem}.drawio"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        args = ["--input", str(input_path), "--output", str(out_file)]

    return _run_script(script, args)


def run_batch(input_dir: Path, output_dir: Path, verbose: bool = False) -> int:
    if not input_dir.is_dir():
        print(f"ERROR: Not a directory: {input_dir}", file=sys.stderr)
        return 1

    files = sorted(
        f
        for f in input_dir.iterdir()
        if f.is_file()
        and f.suffix.lower() in EXTENSION_MAP
        and f.name.lower() != "readme.md"
    )
    if not files:
        print(f"WARNING: No convertible files in {input_dir}", file=sys.stderr)
        return 0

    failed = 0
    for f in files:
        task = detect_task(f)
        print(f"Converting {f.name} ({task})...", file=sys.stderr)
        code = run_task(task, f, output_dir, verbose=verbose)
        if code != 0:
            failed += 1

    return 2 if failed else 0


def main() -> int:
    load_dotenv_if_present()

    parser = argparse.ArgumentParser(
        description="Workflow document conversion — one-click pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python Scripts/convert.py --input Resources/sample.pdf --output output/
  python Scripts/convert.py pdf-to-md --input Resources/a.pdf
  python Scripts/convert.py md-to-docx --input output/report/report.md --template template/default.docx
  python Scripts/convert.py batch --input Resources/ --output output/
        """,
    )
    parser.add_argument(
        "task",
        nargs="?",
        default=None,
        help="Task name or omit for auto-detect from --input extension",
    )
    parser.add_argument("--input", "-i", default=None, help="Input file or directory (batch)")
    parser.add_argument("--output", "-o", default="output", help="Output directory")
    parser.add_argument("--template", "-t", default=None, help="Word template for md-to-docx")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if args.task == "batch":
        if not args.input:
            print("ERROR: batch requires --input directory", file=sys.stderr)
            return 1
        return run_batch(Path(args.input), Path(args.output), args.verbose)

    if not args.input:
        print("ERROR: --input is required", file=sys.stderr)
        return 1

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input not found: {input_path}", file=sys.stderr)
        return 2

    task = args.task or detect_task(input_path)
    return run_task(task, input_path, Path(args.output), args.template, args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
