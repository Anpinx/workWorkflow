# Reference

## Layout Extraction Backends

### Default: Local (no configuration)

PDF and image conversion uses **pymupdf** locally. No API keys, `.env` file, or network access required. Agent should run conversions immediately without asking for credentials.

### Optional: Cloud Layout API (auto-detected)

When `DOCUMENT_LAYOUT_ENDPOINT` and `DOCUMENT_LAYOUT_API_KEY` are present in the **process environment**, the extractor automatically upgrades to cloud layout analysis (`prebuilt-layout` model).

Legacy Azure variable names are also recognized for backward compatibility:

| Variable | Description |
|----------|-------------|
| `DOCUMENT_LAYOUT_ENDPOINT` | Generic cloud layout API endpoint |
| `DOCUMENT_LAYOUT_API_KEY` | API key for the endpoint |
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | Legacy Azure endpoint (alias) |
| `AZURE_DOCUMENT_INTELLIGENCE_KEY` | Legacy Azure key (alias) |

**How to enable (user-initiated only):**

1. User exports env vars in shell, CI secret, or optional `.env` (loaded automatically if present)
2. Re-run conversion — no code or SKILL changes needed

**Agent rule:** Never block conversion on missing credentials. Never create or edit `.env` unless the user explicitly asks.

### Backend Behavior

- **Cloud:** paragraphs (reading order), tables (GFM), figure placeholders
- **Local:** per-page text extraction; embedded PDF images saved to `_assets/`
- **Fallback:** Cloud failure → local extraction with WARNING (exit code still 0)

## draw.io XML Structure

Workflow generates standard mxGraphModel XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" agent="Workflow-document-conversion" version="24.0.0">
  <diagram name="Page-1" id="...">
    <mxGraphModel dx="1200" dy="800" grid="1" ...>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- nodes (vertex="1") and edges (edge="1") -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### JSON Input Schema

```json
{
  "name": "Page-1",
  "nodes": [
    {"key": "A", "label": "Start", "x": 40, "y": 40},
    {"key": "B", "label": "End", "x": 200, "y": 40}
  ],
  "edges": [
    {"source": "A", "target": "B", "label": "next"}
  ]
}
```

### Mermaid Subset

Supported: `flowchart TD`, `graph TD`, `A[Label] --> B[Label]`, edge labels `A -->|text| B`

## Format Mapping Table

| Input | Output | Primary Tool | Output Path |
|-------|--------|--------------|-------------|
| PDF | MD + assets | layout_extractor (local / cloud) | `output/<name>/<name>.md` |
| Image | MD + assets | layout_extractor (local / cloud) | `output/<name>/<name>.md` |
| DOCX | MD | mammoth | `output/<name>/<name>.md` |
| MD | DOCX | python-docx + template | `output/<name>/<name>.docx` |
| XLSX | MD + charts | openpyxl | `output/<name>/<name>.md` |
| PPTX | MD + assets + charts | python-pptx | `output/<name>/<name>.md` |
| JSON/Mermaid | drawio | drawio_writer | user-specified `.drawio` |

## Python Environment

- **Version:** 3.11 (see `.python-version`)
- **Dependencies:** `requirements.txt`
- **Project root imports:** Scripts prepend project root to `sys.path` for `Tools.*`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments / unknown task |
| 2 | File not found / API or IO error |

## Legacy .doc Handling

`.doc` (Word 97-2003) is not supported directly. Pre-convert:

```bash
soffice --headless --convert-to docx Resources/legacy.doc --outdir Resources/
python Scripts/convert.py docx-to-md --input Resources/legacy.docx
```

## Platform Skill Paths

| Platform | Skill Path |
|----------|------------|
| Cursor | `.cursor/skills/document-conversion/SKILL.md` |
| Trae | `.trae/skills/document-conversion/SKILL.md` |
| Claude Code | `.claude/skills/document-conversion/SKILL.md` |
| Codex | `.agents/skills/document-conversion/SKILL.md` |

All copies must stay identical.
