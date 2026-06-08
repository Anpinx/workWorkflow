"""Backward-compatible re-exports; prefer Tools.layout_extractor."""

from Tools.layout_extractor import (  # noqa: F401
    LayoutResult,
    analyze_document,
    discover_cloud_credentials,
    has_azure_credentials,
    has_cloud_credentials,
    log_warnings,
)
