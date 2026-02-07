# BlenderMCP Setup

Connect Claude Desktop to a running Blender instance via the Model Context Protocol for interactive development and testing.

## Prerequisites

- Blender 5.0+ running
- Claude Desktop installed
- `uv` package manager (`brew install uv` on macOS, or `pip install uv`)

## Setup

### 1. Install the Blender Add-on

Download `addon.py` from the [BlenderMCP repo](https://github.com/ahujasid/blender-mcp):

```bash
curl -L -o /tmp/blender_mcp_addon.py \
  https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py
```

In Blender: **Edit > Preferences > Add-ons > Install from Disk** and select the downloaded file. Enable it.

### 2. Configure Claude Desktop

Add this to your Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

### 3. Connect

1. In Blender, open the sidebar panel **BlenderMCP** and click **Start MCP Server** (listens on port 9876)
2. Restart Claude Desktop to pick up the config
3. You should see "blender" in Claude Desktop's MCP tools list

## Usage Notes

- Save your `.blend` file before making changes via Claude
- The first command after connecting sometimes fails — just retry
- For complex operations, break requests into smaller steps
- The MCP connection is a development tool and does not ship with the add-ons
