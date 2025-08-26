# 快速开始指南

## 前置依赖

首先，请先确保您的系统已经安装满足如下要求的软件。

|软件名称|版本要求|说明|
| -- | -- | -- |
|Python|>=3.13|运行 MCP 服务器的基础环境|
|Node.js|>=18.0|Slidev 运行环境|
|UV|-|Python 包管理工具|

### 安装软件

#### 1. 安装 Python（>=3.13）
- 访问 [Python 官网](https://www.python.org/downloads/) 下载并安装最新版本
- 安装时请勾选"Add Python to PATH"选项

#### 2. 安装 UV
```bash
# Windows
pip install uv

# 或者使用官方安装脚本（Linux/macOS）
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 3. 安装 Node.js（>=20.0）
- 访问 [Node.js 官网](https://nodejs.org/) 下载并安装 LTS 版本
- **重要**: 安装时请确保勾选"Add to PATH"选项，将 Node.js 添加到系统 PATH 环境变量中
- 安装完成后在命令行中运行 `node --version` 验证安装
- 如果命令无法识别，可能需要手动将 Node.js 安装目录添加到系统 PATH 中


## 安装项目依赖

### 1. 创建虚拟环境

首先创建虚拟环境，如果您不需要虚拟环境可以跳过该步骤。

```bash
uv venv # 创建虚拟环境
```

### 2. 激活虚拟环境

```bash
# Windows
.venv\Scripts\activate

# Linux/macOS  
source .venv/bin/activate
```

### 3. 安装 Python 依赖

```bash
uv sync  # 安装项目依赖
```

### 4. 安装 Playwright 浏览器

```bash
# 在虚拟环境中安装 Playwright 浏览器
uv run playwright install
```

### 5. 安装 Slidev CLI

```bash
npm install -g @slidev/cli
```

## 验证安装

### 1. 检查环境

运行以下命令检查所有依赖是否正确安装：

```bash
# 检查 Python 版本
python --version

# 检查 Node.js 版本  
node --version

# 检查 UV
uv --version

# 检查 Slidev CLI
slidev --version
```

### 2. 测试 MCP 服务器

```bash
# 激活虚拟环境（如果使用）
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

# 运行 MCP 服务器
uv run servers/themes/academic/server.py
```

如果没有报错，说明服务器启动成功。

> 尝试不同的主题，上面只是展示 `academic` 主题。你可以在 `servers/themes` 目录中找到其他主题。

## 使用指南

### 开发模式

如果您想要进行开发或调试，推荐使用 [OpenMCP](https://marketplace.visualstudio.com/items?itemName=kirigaya.openmcp)：

1. 下载OpenMCP VScode插件。
2. 打开 OpenMCP 插件。
3. 新建MCPServer，选择stdio，配置如下：
   - **命令**: `uv --directory <替换为你的slidev-mcp路径> run main.py`
   - **环境变量**: OpenMCP会自动同步系统的PATH变量，通常不需要手动设置。但如果遇到 Node.js 找不到的问题，需要添加环境变量：
     ```json
     {
       "PATH": "<替换为你的nodejs路径>;${PATH}"
     }
     ```

> **注意**: 
> - 请将 `<替换为你的slidev-mcp路径>` 替换为您实际的项目路径，如 `E:\\node-project\\slidev-mcp`
> - 请将 `<替换为你的nodejs路径>` 替换为您的 Node.js 安装路径，如 `C:\\Program Files\\nodejs`
> - 在某些客户端中，可以使用 `${PATH}` 来引用系统的 PATH 环境变量


### 生产使用

对于日常使用，建议使用 Claude Desktop：

在 Claude Desktop 的配置文件中添加以下配置：

```json
{
  "mcpServers": {
    "slidev-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "<替换为你的slidev-mcp路径>",
        "run",
        "main.py"
      ],
      "env": {
        "PATH": "<替换为你的nodejs路径>;${PATH}"
      },
      "description": "AI-powered Slidev slide creation tool"
    }
  }
}
```

> **注意**: 
> - 请将 `<替换为你的slidev-mcp路径>` 替换为您实际的项目路径，如 `E:\\node-project\\slidev-mcp`
> - 请将 `<替换为你的nodejs路径>` 替换为您的 Node.js 安装路径，如 `C:\\Program Files\\nodejs`
> - `env` 部分用于解决 MCP 客户端找不到 Node.js 的问题
> - `${PATH}` 会引用系统当前的 PATH 环境变量

## 更多功能

安装完成后，您可以：

- 使用自然语言创建幻灯片
- 自动生成专业的 Slidev 演示文稿
- 利用 AI 辅助进行内容编写
- 自定义幻灯片主题和布局

更多使用方法请参考项目的 [README 文档](../README.zh.md)。

## 常见问题 (FAQ)

### Q1: 提示 "Playwright 浏览器未安装" 或 "Executable doesn't exist" 错误？

**解决方法**: 这通常是因为 Playwright 浏览器组件未正确安装导致的。请在激活虚拟环境后运行：

```bash
playwright install
```

### Q2: 为什么一直提示"Node.js 未安装"？

**解决方法**: 这个问题通常发生在 MCP 客户端（如 CherryStudio、Claude Desktop 等）没有继承系统的 PATH 环境变量时。即使 Node.js 在命令行中可以正常使用，MCP 服务器进程也无法找到 Node.js，因为它没有访问系统 PATH 的权限。

#### 对于 CherryStudio 等 MCP 客户端:
配置 MCP 服务器时，需要显式提供 PATH 环境变量：

1. **查找 Node.js 安装路径**:
   - Windows: 通常是 `C:\Program Files\nodejs` 或 `C:\Program Files (x86)\nodejs`
   - macOS: 通常是 `/usr/local/bin` 或 `/opt/homebrew/bin`
   - Linux: 通常是 `/usr/bin` 或 `/usr/local/bin`

2. **配置 MCP 服务器环境变量**:
   在 MCP 客户端配置中添加环境变量部分：
   ```json
   {
     "command": "uv",
     "args": ["--directory", "<替换为你的slidev-mcp路径>", "run", "main.py"],
     "env": {
       "PATH": "<替换为你的nodejs路径>;${PATH}"
     }
   }
   ```

#### 对于 Claude Desktop:
在配置中添加 `env` 部分：
```json
{
  "mcpServers": {
    "slidev-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "<替换为你的slidev-mcp路径>",
        "run",
        "main.py"
      ],
      "env": {
        "PATH": "<替换为你的nodejs路径>;${PATH}"
      },
      "description": "AI-powered Slidev slide creation tool"
    }
  }
}
```

### Q3: 在 Windows 上使用部分工具时出现超时或卡死问题？

**问题说明**: 这是 Windows 系统上使用 stdio 传输模式的已知 bug。该问题主要表现为：
- 在 MCP 服务器的 stdio 模式下调用时出现超时或卡死
- 该问题仅在 Windows 系统上出现

**临时解决方案**:
1. **使用 HTTP 传输模式**: 如果您的 MCP 客户端支持 HTTP 连接，可以尝试使用 HTTP 模式而非 stdio 模式
2. **等待修复**: 开发者正在积极调查这个问题的根本原因并寻找解决方案
3. **系统兼容性**: 在 macOS 和 Linux 系统上不会出现此问题