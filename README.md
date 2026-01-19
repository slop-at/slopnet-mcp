# Slopnet MCP

Post markdown notes ("slops") to a distributed knowledge graph with automatic entity extraction.

## Install

Add to Claude Desktop config (`~/.claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "slopnet": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/slop-at/slopnet-mcp",
        "slopnet-mcp"
      ]
    }
  }
}
```

Then restart Claude Desktop.

## Setup

1. Create a GitHub repo for your slops (e.g., `username/slops`)
2. In Claude: "Hey Claude, setup my slop repo: username/slops"
3. Post your first slop: "Hey Claude, can you slop this for me? Title: Test. Content: ..."

## What you get

- ✅ Markdown files in your GitHub repo
- ✅ Automatic entity extraction (People, Places, Organizations, Events, Topics)
- ✅ Published to knowledge graph at https://slop.at
- ✅ Query with SPARQL

## Configuration

Config is stored at `~/.slop-at/config.json` with default server `https://slop.at`.

## Tools

- `post_slop(title, content, tags)` - Post a slop
- `setup_slop_repo(github_repo)` - First-time setup
- `check_slop_status()` - Check status
- `query_slops(sparql_query)` - Query the graph
- `list_my_slops()` - List your slops

---

Built with ❤️ for the Slopnet collective
