<div align="center">
  <h1>
    <img src="https://api.iconify.design/logos:slidev.svg" width="40" height="40" alt="Slidev"/>
    slidev-mcp 
    <img src="https://api.iconify.design/logos:openai-icon.svg" width="40" height="40" alt="AI"/>
  </h1>
  <p>AI-powered Professional Slide Creation Made Easy!</p>
  
  <p>
    <strong>English</strong> | <a href="README.zh.md">中文</a> | <a href="https://github.com/LSTM-Kirigaya/slidev-ai">Slidev-AI</a>
  </p>
  
  <div>
    <img src="https://img.shields.io/badge/Slidev-@latest-blue?logo=slidev" alt="Slidev"/>
    <img src="https://img.shields.io/badge/AI-Large%20Language%20Model-orange?logo=openai" alt="AI"/>
    <img src="https://img.shields.io/badge/TypeScript-4.9.5-blue?logo=typescript" alt="TypeScript"/>
    <img src="https://img.shields.io/badge/Vue-3.3-green?logo=vue.js" alt="Vue 3"/>
  </div>
</div>

## ✨ Introduction

slidev-mcp is an intelligent slide generation tool based on [Slidev](https://github.com/slidevjs/slidev) that integrates large language model technology, allowing users to automatically generate professional online PPT presentations with simple descriptions.

<img src="https://api.iconify.design/mdi:robot-happy-outline.svg" width="20" height="20" alt="AI"/> **Key Features**:
- Dramatically lowers the barrier to using Slidev
- Natural language interactive slide creation
- Automated generation of professional presentations

We have also open-sourced the AI PPT integrated website project based on slidev-mcp [Slidev-AI](https://github.com/LSTM-Kirigaya/slidev-ai), and you can see the effect in the following video 👇

<a href="https://www.bilibili.com/video/BV1SMhBzJEUL/?spm_id_from=333.1387.homepage.video_card.click&vd_source=3f248073d6ebdb61308992901b606f24" target="_blank"><img src="https://pica.zhimg.com/80/v2-3674ccdc2ceef8255724dbf078cf6ee7_1440w.png" /></a>

## 🚀 Quick Start

For detailed setup and usage instructions, please see [Quick Start Guide](docs/quickstart.md).

### Environment Variable

You can customize the root directory where generated Slidev projects are stored by setting the environment variable `SLIDEV_MCP_ROOT` (MUST be an absolute path). If not set (or set as a non-absolute path), the default relative directory `.slidev-mcp` (under current working directory) is used.

Example (Windows cmd, PowerShell similar):

Projects will then be created under that absolute path instead of `.slidev-mcp/`.

```bash
# powershell
set SLIDEV_MCP_ROOT=my-slides

# bash or zsh
export SLIDEV_MCP_ROOT=my-slides

# then run the script
uv run servers/themes/academic/server.py
```

Projects will then be created under `my-slides/` instead of `.slidev-mcp/`.

## 🔧 Available Tools

The MCP server provides the following tools for slide creation and management:

### Environment & Project Management

| Tool | Input Parameters | Output | Purpose |
|------|------------------|--------|---------|
| `check_environment` | None | Environment status and version info | Verify dependencies are installed |
| `create_slidev` | `path` (str), `title` (str), `author` (str) | Project creation status and path | Initialize new Slidev project |
| `load_slidev` | `path` (str) | Project content and slide data | Load existing presentation |

### Slide Content Management

| Tool | Input Parameters | Output | Purpose |
|------|------------------|--------|---------|
| `make_cover` | `title` (str), `subtitle` (str, opt), `author` (str, opt), `background` (str, opt), `python_string_template` (str, opt) | Cover slide creation status | Create/update cover page |
| `add_page` | `content` (str), `layout` (str, opt) | New slide index | Add new slide to presentation |
| `set_page` | `index` (int), `content` (str), `layout` (str, opt) | Update status | Modify existing slide content |
| `get_page` | `index` (int) | Slide content in markdown | Retrieve specific slide content |

### Utility Tools

| Tool | Input Parameters | Output | Purpose |
|------|------------------|--------|---------|
| `websearch` | `url` (str) | Extracted markdown text | Gather web content for slides |


> **Note**: `opt` = optional parameter

## 📄 License

MIT License © 2023 [LSTM-Kirigaya](https://github.com/LSTM-Kirigaya)
