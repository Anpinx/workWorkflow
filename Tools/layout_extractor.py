"""Document layout extraction with automatic backend selection (local default)."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from Tools.markdown_utils import table_to_gfm

# (endpoint_env, key_env) — first match wins; no .env file required
_CLOUD_CREDENTIAL_PAIRS: tuple[tuple[str, str], ...] = (
    ("DOCUMENT_LAYOUT_ENDPOINT", "DOCUMENT_LAYOUT_API_KEY"),
    ("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "AZURE_DOCUMENT_INTELLIGENCE_KEY"),
)


@dataclass
class LayoutResult:
    """Structured extraction result."""

    markdown: str
    assets: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    backend: str = "local"

    @property
    def used_azure(self) -> bool:
        """Backward-compatible alias for cloud backend usage."""
        return self.backend == "cloud"


def discover_cloud_credentials() -> tuple[str | None, str | None]:
    """Return (endpoint, key) when cloud layout credentials exist in the environment."""
    for endpoint_var, key_var in _CLOUD_CREDENTIAL_PAIRS:
        endpoint = os.environ.get(endpoint_var, "").strip()
        key = os.environ.get(key_var, "").strip()
        if endpoint and key:
            return endpoint, key
    return None, None


def has_cloud_credentials() -> bool:
    endpoint, key = discover_cloud_credentials()
    return bool(endpoint and key)


def has_azure_credentials() -> bool:
    """Backward-compatible alias."""
    return has_cloud_credentials()


def analyze_document(file_path: Path, assets_dir: Path | None = None) -> LayoutResult:
    """
    Analyze PDF or image for layout-aware Markdown.
    Uses local extraction by default; upgrades to cloud layout API when credentials
    are present in the process environment (auto-detected, no config file required).
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input not found: {file_path}")

    endpoint, key = discover_cloud_credentials()
    if endpoint and key:
        try:
            return _analyze_with_cloud(file_path, endpoint, key, assets_dir)
        except Exception as exc:
            warn = f"Cloud layout analysis failed ({exc}); falling back to local extraction."
            result = _analyze_with_local(file_path, assets_dir)
            result.warnings.insert(0, warn)
            return result

    result = _analyze_with_local(file_path, assets_dir)
    result.warnings.insert(
        0,
        "Using local extraction. Scanned PDFs and images may have reduced OCR accuracy.",
    )
    return result


def _analyze_with_cloud(
    file_path: Path,
    endpoint: str,
    key: str,
    assets_dir: Path | None,
) -> LayoutResult:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult
    from azure.core.credentials import AzureKeyCredential

    client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(
            "prebuilt-layout",
            AnalyzeDocumentRequest(bytes_source=f.read()),
        )
    result: AnalyzeResult = poller.result()

    lines: list[str] = []
    warnings: list[str] = []

    if result.paragraphs:
        for para in result.paragraphs:
            content = (para.content or "").strip()
            if not content:
                continue
            role = getattr(para, "role", None)
            if role == "title" or role == "sectionHeading":
                lines.append(f"## {content}")
            else:
                lines.append(content)
            lines.append("")

    if result.tables:
        for idx, table in enumerate(result.tables, start=1):
            lines.append(f"### Table {idx}")
            grid = _table_to_grid(table)
            lines.append(table_to_gfm(grid))
            lines.append("")

    if result.figures and assets_dir:
        assets_dir.mkdir(parents=True, exist_ok=True)
        for idx, _fig in enumerate(result.figures, start=1):
            lines.append(f"![Figure {idx}]({_rel_asset(assets_dir, f'figure_{idx}.png')})")
            lines.append("")
        warnings.append(
            "Figure images referenced as placeholders; re-export from source if needed."
        )

    if not lines and result.content:
        lines.append(result.content)

    markdown = "\n".join(lines).strip() + "\n"
    return LayoutResult(markdown=markdown, warnings=warnings, backend="cloud")


def _table_to_grid(table: Any) -> list[list[str]]:
    rows = table.row_count or 0
    cols = table.column_count or 0
    grid = [["" for _ in range(cols)] for _ in range(rows)]
    for cell in table.cells or []:
        r, c = cell.row_index, cell.column_index
        if r < rows and c < cols:
            grid[r][c] = (cell.content or "").strip()
    return grid


def _analyze_with_local(file_path: Path, assets_dir: Path | None) -> LayoutResult:
    try:
        import fitz  # pymupdf
    except ImportError as exc:
        raise RuntimeError(
            "pymupdf is required for local PDF fallback. Install via: pip install pymupdf"
        ) from exc

    suffix = file_path.suffix.lower()
    warnings: list[str] = []
    assets: list[Path] = []

    if suffix == ".pdf":
        doc = fitz.open(file_path)
        parts: list[str] = []
        for page_num, page in enumerate(doc, start=1):
            parts.append(f"## Page {page_num}")
            parts.append("")
            parts.append(page.get_text("text").strip())
            parts.append("")
            if assets_dir:
                assets_dir.mkdir(parents=True, exist_ok=True)
                for img_idx, img in enumerate(page.get_images(full=True), start=1):
                    xref = img[0]
                    try:
                        pix = fitz.Pixmap(doc, xref)
                        if pix.n - pix.alpha > 3:
                            pix = fitz.Pixmap(fitz.csRGB, pix)
                        out = assets_dir / f"page{page_num}_img{img_idx}.png"
                        pix.save(str(out))
                        assets.append(out)
                        parts.append(
                            f"![Page {page_num} image {img_idx}]({_rel_asset_from_parent(assets_dir, out)})"
                        )
                        parts.append("")
                    except Exception:
                        warnings.append(f"Could not extract image on page {page_num}.")
        doc.close()
        markdown = "\n".join(parts).strip() + "\n"
    else:
        try:
            doc = fitz.open(file_path)
            page = doc[0]
            text = page.get_text("text").strip()
            doc.close()
            markdown = text + "\n" if text else f"<!-- Image: {file_path.name} -->\n"
            if not text:
                warnings.append("No text extracted from image locally; OCR accuracy may be limited.")
        except Exception:
            markdown = f"<!-- Image: {file_path.name} -->\n"
            warnings.append("Could not process image with local extractor.")

    return LayoutResult(markdown=markdown, assets=assets, warnings=warnings, backend="local")


def _rel_asset(assets_dir: Path, name: str) -> str:
    return f"{assets_dir.name}/{name}"


def _rel_asset_from_parent(assets_dir: Path, asset_path: Path) -> str:
    folder = assets_dir.name
    return f"{folder}/{asset_path.name}"


def log_warnings(warnings: list[str], verbose: bool = False) -> None:
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr if verbose else sys.stderr)
