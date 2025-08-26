# Quick Start Guide

## Prerequisites

Please ensure that your system has the following software installed with the specified requirements.

| Software | Version Requirement | Description |
| -- | -- | -- |
| Python | >=3.13 | Base environment for running MCP server |
| Node.js | >=18.0 | Slidev runtime environment |
| UV | - | Python package management tool |

### Software Installation

#### 1. Install Python (>=3.13)
- Visit [Python Official Website](https://www.python.org/downloads/) to download and install the latest version
- Please check "Add Python to PATH" option during installation

#### 2. Install UV
```bash
# Windows
pip install uv

# Or use official installation script (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 3. Install Node.js (>=20.0)
- Visit [Node.js Official Website](https://nodejs.org/) to download and install the LTS version
- **Important**: During installation, ensure "Add to PATH" option is checked to add Node.js to system PATH environment variable
- After installation, run `node --version` in command line to verify the installation
- If the command is not recognized, you may need to manually add Node.js installation directory to your system PATH

## Install Project Dependencies

### 1. Create Virtual Environment

First create a virtual environment. You can skip this step if you don't need a virtual environment.

```bash
uv venv # Create virtual environment
```

### 2. Activate Virtual Environment

```bash
# Windows
.venv\Scripts\activate

# Linux/macOS  
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
uv sync  # Install project dependencies
```

### 4. Install Playwright Browsers

```bash
# Install Playwright browsers in virtual environment
uv run playwright install
```

### 5. Install Slidev CLI

```bash
npm install -g @slidev/cli
```

## Verify Installation

### 1. Check Environment

Run the following commands to check if all dependencies are correctly installed:

```bash
# Check Python version
python --version

# Check Node.js version  
node --version

# Check UV
uv --version

# Check Slidev CLI
slidev --version
```

### 2. Test MCP Server

```bash
# Activate virtual environment (if using)
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

# Run MCP server
uv run servers/themes/academic/server.py
```

If there are no errors, the server has started successfully.

> Try different themes, example above just shows `academic` theme. You can find other themes in `servers/themes` directory.

## Usage Guide

### Development Mode

If you want to develop or debug, we recommend using [OpenMCP](https://marketplace.visualstudio.com/items?itemName=kirigaya.openmcp):

1. Download the OpenMCP VSCode extension.
2. Open the OpenMCP extension.
3. Create a new MCP Server, select stdio, and configure as follows:
   - **Command**: `uv --directory <replace-with-your-slidev-mcp-path> run main.py`
   - **Environment Variables**: If you encounter Node.js not found issues, add environment variables:
     ```json
     {
       "PATH": "<replace-with-your-nodejs-path>;${PATH}"
     }
     ```

> **Note**: 
> - Replace `<replace-with-your-slidev-mcp-path>` with your actual project path, e.g., `E:\\node-project\\slidev-mcp`
> - Replace `<replace-with-your-nodejs-path>` with your Node.js installation path, e.g., `C:\\Program Files\\nodejs`
> - In some clients, you can use `${PATH}` to reference the system's PATH environment variable

### Production Usage

For daily use, we recommend using Claude Desktop:

Add the following configuration to Claude Desktop's configuration file:

```json
{
  "mcpServers": {
    "slidev-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "<replace-with-your-slidev-mcp-path>",
        "run",
        "main.py"
      ],
      "env": {
        "PATH": "<replace-with-your-nodejs-path>;${PATH}"
      },
      "description": "AI-powered Slidev slide creation tool"
    }
  }
}
```

> **Note**: 
> - Replace `<replace-with-your-slidev-mcp-path>` with your actual project path, e.g., `E:\\node-project\\slidev-mcp`
> - Replace `<replace-with-your-nodejs-path>` with your Node.js installation path, e.g., `C:\\Program Files\\nodejs`
> - The `env` section is used to solve Node.js not found issues in MCP clients
> - `${PATH}` references the system's current PATH environment variable

## Additional Features

After installation, you can:

- Create slides using natural language
- Automatically generate professional Slidev presentations
- Use AI assistance for content writing
- Customize slide themes and layouts

For more usage methods, please refer to the project's [README documentation](../README.md).

## Frequently Asked Questions (FAQ)

### Q1: Getting "Playwright browsers not installed" or "Executable doesn't exist" error?

**Solution**: This usually occurs when Playwright browser components are not properly installed. After activating your virtual environment, run:

```bash
playwright install
```

### Q2: Why do I keep getting "Node.js not installed" error?

**Solution**: This issue typically occurs when MCP clients (like CherryStudio, Claude Desktop, etc.) don't inherit the system's PATH environment variables. Even though Node.js works fine in your command prompt/terminal, the MCP server process cannot find Node.js because it doesn't have access to the system PATH.

#### For CherryStudio and similar MCP clients:
When configuring the MCP server, you need to explicitly provide the PATH environment variable:

1. **Find your Node.js installation path**:
   - Windows: Usually `C:\Program Files\nodejs` or `C:\Program Files (x86)\nodejs`
   - macOS: Usually `/usr/local/bin` or `/opt/homebrew/bin`
   - Linux: Usually `/usr/bin` or `/usr/local/bin`

2. **Configure MCP server with environment variables**:
   In your MCP client configuration, add environment variables section:
   ```json
   {
     "command": "uv",
     "args": ["--directory", "<replace-with-your-slidev-mcp-path>", "run", "main.py"],
     "env": {
       "PATH": "<replace-with-your-nodejs-path>;${PATH}"
     }
   }
   ```

#### For Claude Desktop:
Add the `env` section to your configuration:
```json
{
  "mcpServers": {
    "slidev-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "<replace-with-your-slidev-mcp-path>",
        "run",
        "main.py"
      ],
      "env": {
        "PATH": "<replace-with-your-nodejs-path>;${PATH}"
      },
      "description": "AI-powered Slidev slide creation tool"
    }
  }
}
```

### Q3: Experiencing timeout or freezing issues with some tools on Windows?

**Issue Description**: This is a known bug on Windows systems when using stdio transport mode. The issue manifests as:
- Timeout or freezing occurs when called through MCP server in stdio mode
- This issue only occurs on Windows systems

**Temporary Solutions**:
1. **Use HTTP Transport Mode**: If your MCP client supports HTTP connections, try using HTTP mode instead of stdio mode
2. **Wait for Fix**: Developers are actively investigating the root cause of this issue and working on a solution
3. **System Compatibility**: This issue does not occur on macOS and Linux systems

