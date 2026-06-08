---
name: document-conversion
description: >-
  Converts PDF, Word, Excel, PPT, and images to Markdown; generates Word from
  Markdown using templates; exports charts to draw.io (.drawio) XML. Local-first
  extraction (pymupdf, mammoth, openpyxl); optional cloud layout API when env
  credentials are present. Use when converting documents, generating markdown
  content, creating draw.io diagrams, or running Workflow conversion scripts.
compatibility: >-
  Python 3.11+, no API keys required. Windows/macOS/Linux. Word COM not required.
  Optional cloud layout endpoint/key in process environment for higher PDF/OCR fidelity.
metadata:
  author: Workflow
  version: "1.0.0"
  python: "3.11"
---

# Document Conversion

Workflow 文档转换技能：将 Office/PDF/图片转为 Markdown，Markdown 套用模板输出 Word，图表输出 [diagrams.net](https://app.diagrams.net/) 可打开的 `.drawio` 文件。

## Quick Start

```bash
# 1. 创建虚拟环境（Python 3.11）
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# 2. 安装依赖
pip install -r requirements.txt

# 3. 一键转换（无需配置密钥，本地处理即可运行）
python Scripts/convert.py --input Resources/sample.pdf --output output/
```

**退出码：** `0` 成功 · `1` 参数错误 · `2` API/IO 失败

## Project Layout

| Path | Purpose |
|------|---------|
| `Resources/` | 原始素材（PDF、Word、Excel、PPT、图片） |
| `Scripts/` | 转换脚本；入口 `convert.py` |
| `Tools/` | 布局提取、docx 构建、draw.io 生成库 |
| `template/` | Word 样式模板 `default.docx` |
| `output/` | 默认输出目录（gitignore） |

## Decision Tree

根据输入扩展名选择任务（也可显式指定 task）：

| Extension | Task | Script |
|-----------|------|--------|
| `.pdf` | `pdf-to-md` | `Scripts/pdf_to_md.py` |
| `.docx` | `docx-to-md` | `Scripts/docx_to_md.py` |
| `.doc` | `docx-to-md` | 需先转 `.docx`（见 workflows.md） |
| `.xlsx` `.xls` | `xlsx-to-md` | `Scripts/xlsx_to_md.py` |
| `.pptx` `.ppt` | `pptx-to-md` | `Scripts/pptx_to_md.py` |
| `.png` `.jpg` `.jpeg` `.tiff` `.bmp` `.webp` | `image-to-md` | `Scripts/image_to_md.py` |
| `.md` | `md-to-docx` | `Scripts/md_to_docx.py` |
| `.json` `.mmd` `.mermaid` | `chart-to-drawio` | `Scripts/chart_to_drawio.py` |

```bash
# 自动识别扩展名
python Scripts/convert.py --input Resources/report.pdf --output output/

# 显式任务
python Scripts/convert.py pdf-to-md --input Resources/a.pdf --output output/
python Scripts/convert.py md-to-docx --input output/report/report.md --template template/default.docx
python Scripts/convert.py chart-to-drawio --input Resources/flow.json --output output/flow.drawio

# 批量
python Scripts/convert.py batch --input Resources/ --output output/
```

## Content Generation Rules

Agent 生成或编辑内容时遵循：

1. **优先 Markdown** — 所有中间产物与可编辑内容使用 `.md`
2. **Frontmatter 必填** — 生成文件包含 YAML 头：

```yaml
---
title: "Document Title"
source: "Resources/original.pdf"
converter: "pdf_to_md"
generated_at: "2026-06-08T12:00:00+00:00"
---
```

3. **相对路径引用** — 图片 `![alt](basename_assets/img.png)`；图表 `[编辑](charts/flow.drawio)`
4. **标题层级** — 文档标题 `#`；章节 `##`/`###`；勿跳级
5. **表格** — GitHub Flavored Markdown 表格语法
6. **图表** — 流程/架构图输出 `.drawio`，在 MD 中链接而非嵌入二进制

## Format Fidelity

**默认策略：** 直接运行转换脚本，无需配置 `.env` 或平台密钥。脚本自动选择后端（本地 → 可选云端）。

| 场景 | 默认方案 | 精度 |
|------|----------|------|
| PDF 文本/嵌入图 | pymupdf 本地提取 | 中（文本+图片） |
| PDF 布局/表格/OCR | 进程环境中有云端凭证时自动升级 | 高 |
| 图片 OCR | 本地提取；有云端凭证时自动升级 | 低→高 |
| docx → md | mammoth → markdownify | 中（复杂表格需复核） |
| md → docx | python-docx + `template/default.docx` | 高（样式来自模板） |
| xlsx → md | openpyxl | 高（数据）；图表 → draw.io 占位 |
| pptx → md | python-pptx | 中（文本+图片）；图表 → draw.io |

**Agent 动作：** 不要要求用户配置密钥。直接运行 `convert.py`；若 stderr 出现 `WARNING: Using local extraction` 则告知用户扫描件精度可能受限，可选配置云端布局 API（见 reference.md）。

## draw.io Output

- 扩展名：`.drawio`（UTF-8 XML，`mxfile` 根元素）
- 打开方式： [app.diagrams.net](https://app.diagrams.net/) → Open → 选择文件
- 输入格式：JSON `{nodes, edges}` 或 Mermaid `flowchart TD`
- 命名：`output/<basename>/charts/<name>.drawio`
- Markdown 引用：

```markdown
[打开 diagrams.net 编辑](charts/flow.drawio)
```

## Word Template Contract

`template/default.docx` 定义输出样式，**脚本不硬编码字体**。

| Markdown | Word Style |
|----------|------------|
| `#` | Heading 1 |
| `##` | Heading 2 |
| `###` | Heading 3 |
| paragraph | Normal |
| `- item` | List Bullet |
| `1. item` | List Number |
| table | Table Grid |

模板不存在时 `md_to_docx.py` 会自动创建默认模板。

## Validation Checklist

转换完成后逐项确认：

- [ ] 输出 MD 含 frontmatter 且 body 非空
- [ ] 表格行列对齐、无乱码
- [ ] 图片/资产在 `_assets/` 且 MD 链接可解析
- [ ] `.drawio` 可在 diagrams.net 打开
- [ ] `md-to-docx` 输出应用模板 Heading/Normal 样式
- [ ] 本地降级时有 WARNING 日志（非错误，转换仍成功）

## Agent Workflow

1. 确认输入文件在 `Resources/` 或用户提供路径
2. 检查任务类型（Decision Tree）
3. **直接运行** `python Scripts/convert.py --input <path> --output output/ [--verbose]`（无需检查或创建 `.env`）
4. 读取输出 MD，按 Checklist 验证
5. 若 stderr 含本地降级 WARNING 且用户需要高精度 OCR，再说明可选云端配置（reference.md）
6. 若用户需要 Word 终稿：`md-to-docx` + 确认 `template/default.docx`
7. 若含图表：生成或更新 `.drawio`，在 MD 中添加链接

## Additional Resources

- [reference.md](reference.md) — 可选云端布局 API、draw.io XML 结构、格式映射
- [workflows.md](workflows.md) — 各格式详细步骤与边界情况
- [examples.md](examples.md) — 命令与输出示例
