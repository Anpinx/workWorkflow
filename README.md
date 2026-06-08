# Workflow

Workflow 是一个文档转换工具包，内置 Agent Skill **document-conversion**，可在 Cursor、Trae、Claude Code、Codex 等 AI 编程助手中自动或手动触发，完成 PDF/Office/图片 ↔ Markdown、Markdown → Word、图表 → draw.io 等任务。

Workflow is a document conversion toolkit with a built-in Agent Skill **document-conversion**. It works across Cursor, Trae, Claude Code, and Codex to convert PDF/Office/images to Markdown, Markdown to Word, and charts to draw.io—either automatically or on demand.

---

## 环境要求 / Prerequisites

- **Python 3.11+**（与技能 `compatibility` 字段一致 / matches skill metadata）
- Git（克隆仓库 / clone the repo）
- 网络（仅 `pip install` 时需要 / only needed for `pip install`）

### 1. 创建虚拟环境 / Create a virtual environment

```bash
python -m venv .venv
```

**激活 / Activate:**

| 平台 Platform | 命令 Command |
|---------------|--------------|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (cmd) | `.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

### 2. 安装依赖 / Install dependencies

```bash
pip install -r requirements.txt
```

本地转换**无需** API Key 或 `.env` 文件。Local conversion requires **no** API keys or `.env` file.

---

## 快速验证 / Quick Verify

仓库内 `Resources/` 已包含示例文件。任选其一运行：

The repo includes sample files under `Resources/`. Run any supported example:

```bash
# Mermaid → draw.io
python Scripts/convert.py --input Resources/sample-flow.mmd --output output/

# Markdown → Word
python Scripts/convert.py --input Resources/sample-report.md --output output/
```

退出码 / Exit codes：`0` 成功 · `1` 参数错误 · `2` IO/API 失败

---

## 技能概览 / Skill Overview

| 属性 Property | 值 Value |
|---------------|----------|
| 名称 Name | `document-conversion` |
| 路径 Path | 见下方各平台目录 / see platform paths below |

**能力 / Capabilities:**

- PDF、Word、Excel、PPT、图片 → Markdown
- Markdown → Word（套用 `template/default.docx`）
- JSON / Mermaid → draw.io（可在 [diagrams.net](https://app.diagrams.net/) 打开）

**自动触发 / Auto-trigger:** Agent 读取技能 frontmatter 中的 `description`，当任务涉及文档转换、生成 Markdown、创建 draw.io 图表或运行 Workflow 脚本时自动加载完整 `SKILL.md`。

Agents load the full `SKILL.md` when your task matches the skill `description` (document conversion, Markdown generation, draw.io diagrams, or Workflow scripts).

详细工作流见各平台目录下的 `SKILL.md`、`workflows.md`、`examples.md`。

For detailed workflows, see `SKILL.md`, `workflows.md`, and `examples.md` in each platform skill directory.

---

## 各平台使用指南 / Platform Guides

技能已随仓库提交，**克隆或打开项目即可使用**，无需额外安装步骤。

Skills are checked into the repo—clone or open the project and they are ready. No extra install step.

| 平台 Platform | 项目技能路径 Project skill path | 全局技能路径 Global skill path |
|---------------|--------------------------------|--------------------------------|
| **Cursor** | `.cursor/skills/document-conversion/SKILL.md` | `~/.cursor/skills/` |
| **Trae** | `.trae/skills/document-conversion/SKILL.md` | `~/.trae/skills/`（国际版）或 `~/.trae-cn/skills/`（国内版） |
| **Claude Code** | `.claude/skills/document-conversion/SKILL.md` | `~/.claude/skills/` |
| **Codex** | `.agents/skills/document-conversion/SKILL.md` | `~/.agents/skills/` |

### Cursor

1. 用 Cursor 打开 Workflow 项目根目录。Open the Workflow project root in Cursor.
2. Agent 会话启动时会索引 `.cursor/skills/` 下所有技能的 `name` 与 `description`。On session start, Cursor indexes skill names and descriptions under `.cursor/skills/`.
3. 在 Agent 对话中用自然语言描述任务即可，例如：In Agent chat, describe the task in natural language, for example:
   - 「把 `Resources/sample-report.md` 转成 Word」
   - “Convert `Resources/sample-flow.mmd` to a draw.io diagram”
4. Agent 匹配到 `document-conversion` 后会读取 `SKILL.md` 并按其中流程执行 `Scripts/convert.py`。

**说明 / Notes:** 项目级技能位于 `.cursor/skills/`；个人全局技能放在 `~/.cursor/skills/`，对所有项目生效。Project skills live in `.cursor/skills/`; personal skills in `~/.cursor/skills/` apply to all projects.

### Trae

1. 用 Trae 打开 Workflow 项目。Open Workflow in Trae.
2. Trae 自动加载 `.trae/skills/` 下的技能索引；任务匹配时注入完整 `SKILL.md`。Trae auto-loads the skill index; the full `SKILL.md` is injected when the task matches.
3. **显式调用 / Explicit invoke:** 在聊天中输入 `/document-conversion` 将技能加入当前对话上下文。Type `/document-conversion` in chat to add the skill to context.
4. 自然语言示例 / Example prompts:
   - 「批量转换 Resources 目录下的文档」
   - “Convert this PDF to Markdown and check the output”

**说明 / Notes:**

- 国际版 Trae（trae.ai）全局技能目录为 `~/.trae/skills/`；国内版（trae.cn）为 `~/.trae-cn/skills/`。
- 可在 Trae Skills 面板浏览、安装或上传本地技能；本仓库技能已内置，无需再装。

### Claude Code

1. 在项目根目录启动 Claude Code（`claude` CLI 或 IDE 集成）。Start Claude Code from the project root.
2. Claude 从 `.claude/skills/` 向上遍历至仓库根目录发现项目技能。Claude discovers project skills from `.claude/skills/` up to the repo root.
3. **显式调用 / Explicit invoke:** `/document-conversion`
4. 自然语言示例 / Example prompts:
   - 「运行 convert.py 把 report.pdf 转成 Markdown」
   - “Generate Word from the converted Markdown using the default template”

**说明 / Notes:**

- 首次加载含 `.claude/skills/` 的项目时，可能需要接受 **workspace trust** 对话框。
- 个人全局技能：`~/.claude/skills/`。

### Codex

1. 在 Workflow 仓库内启动 Codex CLI 或 IDE 扩展。Start Codex CLI or the IDE extension inside the Workflow repo.
2. Codex 从当前工作目录向上扫描至仓库根，读取 `.agents/skills/` 中的技能。Codex scans from the cwd up to the repo root for skills in `.agents/skills/`.
3. **显式调用 / Explicit invoke:**
   - CLI/IDE 中输入 `$document-conversion` 或通过 `/skills` 选择
   - Type `$document-conversion` or pick the skill via `/skills`
4. 自然语言示例 / Example prompts:
   - 「用 Workflow 把 Excel 转成 Markdown」
   - “Convert images in Resources to Markdown with verbose logging”

**说明 / Notes:**

- 个人全局技能：`~/.agents/skills/`（或 Codex 文档中的 `$HOME/.agents/skills`）。
- 可选：在技能目录添加 `agents/openai.yaml`，设置 `policy.allow_implicit_invocation: false` 可限制为仅手动 `$skill` 调用（本仓库未包含该文件）。Optionally add `agents/openai.yaml` with `policy.allow_implicit_invocation: false` to require explicit `$skill` invocation (not included in this repo).

---

## 可选配置 / Optional Config

默认本地转换**不需要**任何环境变量。Default local conversion needs **no** environment variables.

若需更高精度的 PDF 布局分析或 OCR，可在 shell 或 CI 中设置（也可写入项目根 `.env`，脚本会自动加载）：

For higher-fidelity PDF layout or OCR, set in your shell or CI (or in a root `.env`, loaded automatically):

| 变量 Variable | 说明 Description |
|---------------|------------------|
| `DOCUMENT_LAYOUT_ENDPOINT` | 云端布局 API 端点 / cloud layout API endpoint |
| `DOCUMENT_LAYOUT_API_KEY` | API 密钥 / API key |

详见 [`.env.example`](.env.example) 与各技能目录中的 `reference.md`。

See [`.env.example`](.env.example) and `reference.md` in any skill directory.

---

## 技能同步维护 / Keeping Skills in Sync

修改技能内容时，请同步更新以下 **4 个目录**（文件应保持一致）：

When editing skill content, update all **4** directories (files must stay identical):

```
.cursor/skills/document-conversion/
.trae/skills/document-conversion/
.claude/skills/document-conversion/
.agents/skills/document-conversion/
```

每个目录包含 / Each directory contains:

- `SKILL.md` — 主指令 / main instructions
- `reference.md` — 可选 API、格式映射、平台路径 / optional API, format mapping, platform paths
- `workflows.md` — 分格式工作流 / per-format workflows
- `examples.md` — 命令示例 / command examples

---

## 进一步阅读 / Further Reading

- 技能主文档 / Skill docs: `.cursor/skills/document-conversion/SKILL.md`（四平台副本相同 / same in all four locations）
- 环境变量示例 / Env example: [`.env.example`](.env.example)
- Agent Skills 规范 / Agent Skills spec: [agentskills/agentskills](https://github.com/agentskills/agentskills)
