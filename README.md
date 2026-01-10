# Axon Bridge MCP Server

A high-performance [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that acts as an intelligent bridge between LLMs and [Axon Server](https://github.com/repolex-ai/axon-server). This server enables AI agents to interact with a remote or local Axon instance via standardized SPARQL queries and updates.

---

## 🚀 Features

* **HTTP Bridge Architecture:** Connects to [Axon Server](https://github.com/repolex-ai/axon-server) via its native HTTP SPARQL endpoints.
* **Deterministic Environments:** Powered by [uv](https://astral.sh/uv) and a verified `uv.lock` for reproducible, crash-free deployments.
* **Full SPARQL 1.1 Support:** Supports complex `SELECT` queries for data retrieval and `UPDATE` operations for graph management.
* **Asynchronous Core:** Built with `httpx` and `FastMCP` for high-concurrency tool execution.

---

## 📦 Installation

### 1. Prerequisites

* **Windows 11**
* **[uv](https://astral.sh/uv)** (Python package manager). Install via PowerShell:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

```


* **Axon Server:** A running instance of [Axon Server](https://github.com/repolex-ai/axon-server) (typically on port `7878`).

### 2. Setup

Clone the repository and synchronize the environment:

```powershell
git clone https://github.com/repolex-ai/axon-bridge-mcp.git
cd axon-bridge-mcp
uv sync

```

---

## 🛠 Usage

### Running the Server

You can run the server directly using the project's locked virtual environment:

```powershell
uv run python server.py

```

### Testing & Inspection

Use the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) to verify your tools visually:

```powershell
npx @modelcontextprotocol/inspector uv run python server.py

```

---

## 🔌 Claude Desktop Integration

To use this bridge within the Claude Desktop app, update your `%APPDATA%\Claude\claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "axon-bridge": {
      "command": "uv",
      "args": [
        "--directory", "C:/absolute/path/to/axon-bridge-mcp",
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

## 🧰 Available Tools

| Tool | Description | Arguments |
| --- | --- | --- |
| `query_graph` | Executes a SPARQL `SELECT` query against the Axon store. | `sparql_query` (string) |
| `update_graph` | Executes a SPARQL `UPDATE` (INSERT/DELETE) operation. | `sparql_update` (string) |

---

## 📖 Usage Examples

### AI-Driven Retrieval

The AI can autonomously explore your graph using standard patterns:

```sparql
PREFIX schema: <https://schema.org/>
SELECT ?name ?version WHERE {
  ?s a schema:SoftwareApplication ;
     schema:name ?name ;
     schema:softwareVersion ?version .
}

```

### Extending the Knowledge Graph

Insert new metadata directly through the chat interface:

```sparql
PREFIX schema: <https://schema.org/>
INSERT DATA {
  <https://example.com/project> a schema:CreativeWork ;
    schema:name "My New Project" ;
    schema:author "Israel" .
}

```
