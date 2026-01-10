# Axon Bridge MCP Server

An agentic [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for Windows 11 that bridges LLMs with [Axon Server](https://github.com/repolex-ai/axon-server) and automates Git workflows.

## 🚀 Core Capabilities
- **Graph Ops:** Native SPARQL query/update via Axon Server.
- **Hidden Storage:** Manages a persistent `.axon-repo` in the user's home directory for hidden configurations.
- **Smart Git Workflow:** Staging, diff analysis, branch management, and AI-summarized commits.

## 📦 Setup

### 1. Prerequisites
- **uv** installed (`powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`)
- **Git** installed and in your PATH.
- **Axon Server** running on `localhost:7878`.

### 2. Installation
```powershell
git clone [https://github.com/repolex-ai/axon-bridge-mcp.git](https://github.com/repolex-ai/axon-bridge-mcp.git)
cd axon-bridge-mcp
uv sync

```

### 3. Initialize Hidden Repo

The AI can guide you, or you can run this now:

```powershell
mkdir ~/.axon-repo
attrib +h ~/.axon-repo

```

## 🔌 Claude Desktop Integration

Update `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "axon-bridge": {
      "command": "uv",
      "args": ["--directory", "C:/path/to/axon-bridge-mcp", "run", "python", "server.py"],
      "env": {
        "AXON_HOST": "localhost",
        "AXON_PORT": "7878"
      }
    }
  }
}

```

## 🛠 Workflow Tools

| Tool | Description |
| --- | --- |
| `query_graph` | Query the RDF knowledge graph. |
| `check_axon_repo` | Inspect the hidden `.axon-repo` folder. |
| `get_staged_diff` | Summarize code changes before committing. |
| `git_commit` | Save changes with AI-generated messages. |

```
