# Slopnet MCP Installation

## Quick Install

### Step 1: Install with uv

```bash
uv tool install git+https://github.com/slop-at/slopnet-mcp
```

This downloads and installs all dependencies (~150MB). Takes 1-2 minutes on first run.

### Step 2: Add to Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "slopnet": {
      "command": "slopnet-mcp"
    }
  }
}
```

### Step 3: Restart Claude Desktop

That's it! The MCP should connect successfully.

## First-Time Setup

1. Create a GitHub repo for your slops (e.g., `your-username/slops`)
2. In Claude: "Hey Claude, setup my slop repo: your-username/slops"
3. Post your first slop!

## Updating

```bash
uv tool upgrade slopnet-mcp
```

## Uninstalling

```bash
uv tool uninstall slopnet-mcp
```

## Troubleshooting

**Check if it's installed:**
```bash
which slopnet-mcp
# Should show: ~/.local/bin/slopnet-mcp
```

**Test the server:**
```bash
slopnet-mcp
# Should start the MCP server
```

**Reinstall if needed:**
```bash
uv tool uninstall slopnet-mcp
uv tool install git+https://github.com/slop-at/slopnet-mcp
```
