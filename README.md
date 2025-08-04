<div align="center">
  <h1>
    <img src="https://api.iconify.design/logos:slidev.svg" width="40" height="40" alt="Slidev"/>
    slidev-mcp 
    <img src="https://api.iconify.design/logos:openai-icon.svg" width="40" height="40" alt="AI"/>
  </h1>
  <p>AI-powered Professional Slide Creation Made Easy!</p>
  
  <p>
    <strong>English</strong> | <a href="README.zh.md">中文</a>
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

## 🚀 Quick Start

For detailed setup and usage instructions, please see [Quick Start Guide](docs/quickstart.md).

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