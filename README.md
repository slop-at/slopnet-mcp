# mcp-slop

**Slopnet MCP Server** - Post knowledge "slops" to a distributed knowledge graph with automatic entity extraction.

## What's a Slop?

A **slop** is a markdown note with:
- Frontmatter metadata (title, author, tags)
- Your thoughts, ideas, or knowledge
- Auto-extracted entities (people, places, concepts)
- Public GitHub URL for discoverability

When you post a slop, it's automatically:
1. Saved as markdown in your GitHub repo
2. Analyzed with GLiNER2 NER (using [know.dev ontology](https://know.dev))
3. Published to the Slopnet knowledge graph
4. Pushed to GitHub for public access

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/repolex-ai/axon-bridge-mcp.git mcp-slop
cd mcp-slop
uv sync
```

### 2. First-Time Setup

Create a GitHub repo for your slops (e.g., `username/slops`), then in Claude:

```
Hey Claude, can you setup my slop repo? It's goodlux/slop
```

Claude will call `setup_slop_repo("goodlux/slop")` which clones it to `~/.axon-repo/goodlux/slop`.

### 3. Post Your First Slop!

```
Hey Claude, can you slop this for me?

Title: Thoughts on Knowledge Graphs
Content: Knowledge graphs are a powerful way to represent...
```

Claude calls `post_slop()` which:
- Creates `a3f2e1b9.md` (UUID-based filename)
- Extracts entities (Person, Organization, DefinedTerm, etc.)
- Builds RDF graph with provenance
- Commits & pushes to GitHub
- Posts to graph server (default: https://slop.at)

## 🔌 Claude Desktop Integration

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "slopnet": {
      "command": "uv",
      "args": [
        "--directory", "/Users/you/mcp-slop",
        "run", "python", "server.py"
      ],
      "env": {
        "SLOP_GRAPH_SERVER": "https://slop.at"
      }
    }
  }
}
```

## 🛠 Available Tools

### Core
- **`post_slop(title, content, tags)`** - Post a slop with entity extraction
- **`setup_slop_repo(github_repo)`** - First-time repo setup
- **`check_slop_status()`** - Check config and status

### Query
- **`query_slops(sparql_query)`** - Query the knowledge graph
  - "What has Izzy posted lately?"
  - "Who's writing about AI?"
  - "Show me slops about semantic web"

### Management
- **`list_my_slops()`** - List your local slops
- **`update_graph(sparql_update)`** - Advanced graph operations

## 📊 Knowledge Graph

Slops are published as RDF using:
- **know.dev** ontology for entity types (Person, Organization, Event, Place)
- **Schema.org** for properties
- **Nepomuk NFO** for file metadata
- Custom **Slop** ontology for provenance

Example query:

```sparql
PREFIX slop: <https://slop.at/ontology#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?slop ?title ?author
WHERE {
  ?slop a slop:Slop ;
        dcterms:title ?title ;
        dcterms:creator ?author .
}
ORDER BY DESC(?slop)
LIMIT 10
```

## 🧠 Entity Extraction

Uses [GLiNER2](https://github.com/fastino/gliner2) with know.dev ontology:

**Entity Types:**
- Person, Organization, Company
- Place, Event, Meeting, Conference
- DefinedTerm, Topic
- Family, Community

**Extracted Data:**
- Entity text & type
- Line numbers (for GitHub links)
- Confidence scores
- Relationships (coming soon!)

## 🗂 File Structure

```
~/.axon-repo/
├── config.json              # Your config
└── {org}/{repo}/            # Your slop repo
    ├── a3f2e1b9.md         # Slop files (UUID-based)
    └── b4d8c2a1.md

mcp-slop/
├── server.py               # MCP tools
├── config.py               # Config management
├── repo.py                 # Git operations
├── extraction.py           # GLiNER2 + RDF
└── ontology/
    └── know.ttl           # know.dev ontology
```

## 🎯 Use Cases

1. **Personal Knowledge Management**
   - Post notes from conversations
   - Extract entities automatically
   - Query your knowledge graph

2. **Collaborative Research**
   - Share slops publicly on GitHub
   - Query "who's working on similar topics?"
   - Build a distributed research network

3. **AI Memory**
   - Give Claude a persistent knowledge base
   - Query past conversations and insights
   - Build context across sessions

## 🔧 Configuration

Config is stored in `~/.axon-repo/config.json`:

```json
{
  "graph_server": "https://slop.at",
  "github_repo": "goodlux/slop",
  "github_username": "goodlux",
  "real_name": "Goodlux McSlop"
}
```

Override graph server with env var:
```bash
export SLOP_GRAPH_SERVER="http://localhost:7878"
```

## 📝 Frontmatter Format

```yaml
---
title: Your Slop Title
author: goodlux
created: 2026-01-16T03:14:15
tags: [slop, knowledge-graphs, ai]
slop_id: a3f2e1b9-4c2d-4e8f-9a1b-3c4d5e6f7a8b
---

Your markdown content here...
```

Compatible with Obsidian!

## 🚧 Roadmap

- [ ] Relation extraction (knows, worksFor, etc.)
- [ ] Slop updates (`update_slop` tool)
- [ ] Slop deletion (`delete_slop` tool)
- [ ] Web UI for browsing slops
- [ ] Federation (query multiple Slopnet servers)
- [ ] OIDC authentication for private slops

---

Built by spacegoatai 🐐✨ for the Slopnet collective
