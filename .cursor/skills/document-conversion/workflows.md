# Workflows

## PDF → Markdown

```bash
python Scripts/convert.py pdf-to-md --input Resources/report.pdf --output output/ --verbose
```

**Steps:**
1. Auto-select backend: local (default) or cloud (if env credentials detected)
2. Extract paragraphs (reading order), tables (GFM), figure placeholders
3. Write `output/report/report.md` + `report_assets/`

**Local default:** pymupdf extracts plain text per page; embedded images saved to `_assets/`. No setup required.

## Image → Markdown

```bash
python Scripts/convert.py image-to-md --input Resources/scan.png --output output/
```

Same layout pipeline as PDF. Runs locally by default; cloud OCR when env credentials present.

## Word → Markdown

```bash
python Scripts/convert.py docx-to-md --input Resources/doc.docx --output output/
```

**Limitations:**
- Complex nested tables may lose structure — add `<!-- 需人工复核 -->` in output
- Embedded OLE objects not converted
- `.doc` requires LibreOffice pre-conversion (see reference.md)

## Markdown → Word

```bash
python Scripts/convert.py md-to-docx \
  --input output/report/report.md \
  --template template/default.docx \
  --output output/
```

**Steps:**
1. Strip YAML frontmatter
2. Parse MD blocks (headings, lists, tables, paragraphs)
3. Apply styles from template (not hardcoded fonts)
4. Save `output/report/report.docx`

**Customize template:** Edit `template/default.docx` in Word — preserve style names in reference.md.

## Excel → Markdown

```bash
python Scripts/convert.py xlsx-to-md --input Resources/data.xlsx --output output/
```

- One `## SheetName` section per sheet
- Sheet data as GFM table
- Embedded charts → placeholder `.drawio` in `charts/` with MD link

## PowerPoint → Markdown

```bash
python Scripts/convert.py pptx-to-md --input Resources/deck.pptx --output output/
```

- One `## Slide N: Title` per slide
- Text frames extracted as paragraphs
- Pictures → `_assets/slideN_imgM.png`
- Charts → `charts/slideN_chartM.drawio`

## Chart → draw.io

```bash
# From JSON
python Scripts/chart_to_drawio.py --input Resources/flow.json --output output/flow.drawio

# From Mermaid
python Scripts/chart_to_drawio.py --input Resources/flow.mmd --output output/flow.drawio
```

Open result at [app.diagrams.net](https://app.diagrams.net/).

## Batch Conversion

```bash
python Scripts/convert.py batch --input Resources/ --output output/
```

Processes all supported files in directory. Skips unsupported extensions. Returns exit code 2 if any file fails.

## End-to-End: PDF → MD → DOCX

```bash
python Scripts/convert.py --input Resources/report.pdf --output output/
python Scripts/convert.py md-to-docx --input output/report/report.md --template template/default.docx
```

## Agent Content Generation Workflow

When **creating** content (not just converting):

1. Draft in Markdown with frontmatter
2. Save to `output/<topic>/<topic>.md`
3. Add diagrams as JSON/Mermaid → run `chart-to-drawio`
4. Link diagrams in MD
5. Optional final Word: `md-to-docx`
6. Run Validation Checklist from SKILL.md
