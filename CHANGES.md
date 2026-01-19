# Changes for Production Release

## Bug Fixes

1. **Added missing `get_graph_server_url()` function** (server.py:22-28)
   - Was being called but never defined
   - Supports both `SLOP_WEB_SERVER` and `SLOP_GRAPH_SERVER` env vars
   - Falls back to config.json then default

2. **Fixed slop_id consistency** (server.py:52-53, 136, 146)
   - Now consistently 8 chars everywhere
   - No redundant slicing

3. **Unified server URL handling**
   - All tools use `get_graph_server_url()`
   - Consistent configuration priority

## Changes

1. **Simplified README** - Barebones install, no BS
2. **Updated pyproject.toml** - Ready for `uv tool install`
3. **Added LICENSE** - MIT
4. **Updated GitHub org** - Changed from `your-org` to `slop-at`
5. **Added complete Claude Desktop config** - Copy-paste ready with env var

## Install

Users just add this to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "slopnet": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/slop-at/slopnet-mcp",
        "slopnet-mcp"
      ],
      "env": {
        "SLOP_WEB_SERVER": "https://slop.at"
      }
    }
  }
}
```

Done. Restart Claude Desktop.
