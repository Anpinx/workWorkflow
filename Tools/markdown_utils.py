"""Markdown frontmatter and path utilities."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def project_root() -> Path:
    """Return Workflow project root (parent of Tools/)."""
    return Path(__file__).resolve().parent.parent


def load_dotenv_if_present() -> None:
    """Load .env from project root when python-dotenv is available."""
    try:
        from dotenv import load_dotenv

        env_path = project_root() / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass


def ensure_output_dir(output: Path, basename: str) -> Path:
    """Create output/<basename>/ and return that path."""
    out_dir = output / basename
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def relative_link(from_dir: Path, target: Path) -> str:
    """POSIX-style relative path for markdown links."""
    return Path(
        Path(from_dir).resolve().relative_to(Path(from_dir).resolve().anchor)
        if False
        else target
    ).as_posix() if False else _rel(from_dir, target)


def _rel(from_dir: Path, target: Path) -> str:
    try:
        return Path(
            Path(target).resolve().relative_to(Path(from_dir).resolve())
        ).as_posix()
    except ValueError:
        return Path(target).as_posix()


def build_frontmatter(
    title: str,
    source: str,
    converter: str,
    extra: dict[str, str] | None = None,
) -> str:
    """Build YAML frontmatter block for generated markdown."""
    lines = [
        "---",
        f'title: "{_escape_yaml(title)}"',
        f"source: {_escape_yaml(source)}",
        f"converter: {converter}",
        f'generated_at: "{datetime.now(timezone.utc).isoformat()}"',
    ]
    if extra:
        for key, value in extra.items():
            lines.append(f"{key}: {_escape_yaml(str(value))}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def _escape_yaml(value: str) -> str:
    if any(c in value for c in ':"\\{}[]&*#?|-<>=!%@`'):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def strip_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter dict, body) from markdown text."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip('"')
    body = text[match.end() :]
    return meta, body


def table_to_gfm(rows: list[list[str]]) -> str:
    """Convert 2D string grid to GitHub Flavored Markdown table."""
    if not rows:
        return ""

    width = max(len(r) for r in rows)
    normalized = [r + [""] * (width - len(r)) for r in rows]

    def esc(cell: str) -> str:
        return cell.replace("|", "\\|").replace("\n", " ").strip()

    header = normalized[0]
    lines = [
        "| " + " | ".join(esc(c) for c in header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in normalized[1:]:
        lines.append("| " + " | ".join(esc(c) for c in row) + " |")
    return "\n".join(lines)
