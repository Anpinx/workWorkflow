#!/usr/bin/env python3
"""Convert chart definitions (JSON/Mermaid) to draw.io (.drawio) XML."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Tools.drawio_writer import load_input, write_drawio


def convert(input_path: Path, output_path: Path | None = None) -> Path:
    input_path = Path(input_path)
    if output_path:
        out = Path(output_path)
    else:
        out = input_path.with_suffix(".drawio")

    diagram = load_input(input_path)
    return write_drawio(diagram, out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Chart to draw.io")
    parser.add_argument("--input", "-i", required=True, help="JSON or .mmd input")
    parser.add_argument("--output", "-o", default=None, help="Output .drawio path")
    args = parser.parse_args()

    try:
        out = convert(Path(args.input), Path(args.output) if args.output else None)
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
