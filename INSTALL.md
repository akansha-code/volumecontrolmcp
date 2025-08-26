# 🎯 Quick Setup Guide

## For End Users (Simple)

### 1. Install
```bash
pip install volumecontrolmcp
```

### 2. Add to your MCP client config
```json
{
  "servers": {
    "volumecontrol": {
      "command": "volumecontrolmcp"
    }
  }
}
```

### 3. Use!
You now have volume control tools in your MCP client.

## For Claude Desktop Users

1. Install: `pip install volumecontrolmcp`

2. Edit config file:
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

3. Add this:
```json
{
  "mcpServers": {
    "volumecontrol": {
      "command": "volumecontrolmcp"
    }
  }
}
```

4. Restart Claude Desktop

## For Developers

```bash
git clone https://github.com/akansha-code/volumecontrolmcp.git
cd volumecontrolmcp
pip install -e .
```

That's it! 🚀
