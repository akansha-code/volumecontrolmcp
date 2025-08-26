# Volume Control MCP Server

A **Model Context Protocol (MCP) Server** for Windows volume control that can be easily installed and configured with any MCP client.

## 🚀 Quick Installation & Setup

### 1. Install the Package

```bash
# Install from PyPI (when published)
pip install volumecontrolmcp

# Or install from source
pip install git+https://github.com/akansha-code/volumecontrolmcp.git
```

### 2. Configure Your MCP Client

Add this to your MCP client configuration file (e.g., `mcp.json`, Claude Desktop config, etc.):

```json
{
  "servers": {
    "volumecontrol": {
      "command": "volumecontrolmcp"
    }
  }
}
```

### 3. For Claude Desktop Users

Add this to your Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "volumecontrol": {
      "command": "volumecontrolmcp"
    }
  }
}
```

### 4. That's it! 🎉

Your volume control server is now available in your MCP client with 6 tools, 3 resources, and 3 prompts.

## ✨ Features

- **6 Tools:** `get_volume`, `set_volume`, `mute`, `unmute`, `toggle_mute`, `apply_preset`
- **3 Resources:** Real-time state, presets, capabilities
- **3 Prompts:** Help, settings, troubleshooting
- **5 Presets:** MUTED, LOW, MEDIUM, HIGH, MAX

## 🔧 Manual Server Start

If you need to run the server manually:

```bash
volumecontrolmcp
```

## 📋 Requirements

- Windows OS
- Python 3.10+
- Audio drivers installed

## 🛠️ Development

```bash
git clone https://github.com/akansha-code/volumecontrolmcp.git
cd volumecontrolmcp
pip install -e ".[dev]"
```

## 📖 Full Documentation

For complete API documentation, troubleshooting, and examples, see the [full README](https://github.com/akansha-code/volumecontrolmcp#readme).

---

**Easy installation → Simple configuration → Volume control in your MCP client!**
