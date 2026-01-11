# Axon Bridge MCP

A specialized [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for Windows 11 designed to bridge LLMs with [Axon Server](https://github.com/repolex-ai/axon-server). This node automates the **Slopnet** workflow: compressing complex ideas into portable, metadata-rich Markdown "slops" and synchronizing them via Git and SPARQL.

## 🚀 Core Features

* **Slop Generation:** Automates creation of [structured Markdown files](https://github.com/repolex-ai/axon-bridge-mcp/commit/0cc32f2d8dd4c905c9c5f191914a949a4bd2bf4b) with YAML frontmatter for Obsidian and Axon indexing.
* **Knowledge Graph Ops:** Native SPARQL query and update capabilities via the [Axon Server](https://github.com/repolex-ai/axon-bridge-mcp/commit/0cc32f2d8dd4c905c9c5f191914a949a4bd2bf4b) HTTP endpoint.
* **Agentic Git Workflow:** Full lifecycle management including branch creation, staging, [Smart Commits](https://github.com/repolex-ai/axon-bridge-mcp/commit/0cc32f2d8dd4c905c9c5f191914a949a4bd2bf4b), and automated [GitHub pushes](https://github.com/repolex-ai/axon-bridge-mcp/commit/0cc32f2d8dd4c905c9c5f191914a949a4bd2bf4b).
* **Hidden Workspace:** Manages a persistent `~/.axon-repo` for secure, hidden "agentic memory" and configuration.

---

## 📦 Installation & Setup

### 1. Prerequisites

* **[uv](https://astral.sh/uv)** installed (Recommended for speed and environment isolation).
* **Git** installed and accessible in your Windows PATH.
* **Axon Server** running locally on port `7878`.

### 2. Quick Start

```powershell
git clone https://github.com/repolex-ai/axon-bridge-mcp.git
cd axon-bridge-mcp
uv sync

```

---

## ⚡ Lightweight Running Options

You can run this MCP server in several ways depending on your system resources and workflow needs:

### Option A: The "uv" Standard (Recommended)

This is the fastest and most stable method. It uses the `uv.lock` file to ensure a deterministic environment without manual activation.

```powershell
uv run python server.py

```

### Option B: The "Dev-Inspector" Mode

Best for debugging or visual testing of tools. This launches a web-based UI to interact with your server tools individually.

```powershell
npx @modelcontextprotocol/inspector uv run python server.py

```

### Option C: Standalone Python (No-uv)

If you prefer traditional virtual environments, you can run it using standard Python tools:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python server.py

```

---

## 🔌 Claude Desktop Integration

To use this bridge with Claude, add the following to your `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "axon-bridge": {
      "command": "uv",
      "args": [
        "--directory", "C:/path/to/axon-bridge-mcp",
        "run", "python", "server.py"
      ],
      "env": {
        "AXON_HOST": "localhost",
        "AXON_PORT": "7878"
      }
    }
  }
}

```

---

## 🛠 Available Tools

| Tool | Description |
| --- | --- |
| `create_slop` | Generates a Markdown file with [metadata frontmatter](https://github.com/repolex-ai/axon-bridge-mcp/commit/0cc32f2d8dd4c905c9c5f191914a949a4bd2bf4b). |
| `git_push` | Syncs your local [commits to GitHub](https://github.com/repolex-ai/axon-bridge-mcp/commit/0cc32f2d8dd4c905c9c5f191914a949a4bd2bf4b) for public discovery. |
| `query_graph` | Executes [SPARQL SELECT queries](https://github.com/repolex-ai/axon-bridge-mcp/commit/0cc32f2d8dd4c905c9c5f191914a949a4bd2bf4b) against Axon. |
| `update_graph` | Performs [SPARQL UPDATE operations](https://github.com/repolex-ai/axon-bridge-mcp/commit/0cc32f2d8dd4c905c9c5f191914a949a4bd2bf4b) to modify the graph. |
| `check_axon_repo` | Verifies and [lists the contents](https://github.com/repolex-ai/axon-bridge-mcp/commit/0cc32f2d8dd4c905c9c5f191914a949a4bd2bf4b) of the hidden workspace. |
