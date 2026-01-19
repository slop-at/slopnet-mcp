# Slopnet MCP

Post markdown notes to a distributed knowledge graph with automatic entity extraction.

## Install

```bash
uv tool install git+https://github.com/slop-at/slopnet-mcp
```

Add to Claude Desktop config:

**macOS/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "slopnet": {
      "command": "uv",
      "args": ["tool", "run", "slopnet-mcp"]
    }
  }
}
```

Restart Claude Desktop.

## Setup

1. Create a GitHub repo for your slops
2. In Claude: "setup my slop repo: username/slops"
3. Post a slop: "slop this. Title: Test. Content: ..."

## Tools

- `post_slop(title, content, tags)`
- `setup_slop_repo(github_repo)`
- `check_slop_status()`
- `query_slops(sparql_query)`
- `list_my_slops()`
