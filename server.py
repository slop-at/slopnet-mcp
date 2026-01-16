import os
import uuid
import datetime
import httpx
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from config import SlopConfig
from repo import RepoManager
from extraction import extract_entities, build_rdf_graph, graph_to_ntriples

# Initialize FastMCP
mcp = FastMCP("SlopNet")

# Configuration
config = SlopConfig()
repo_manager = RepoManager(config)

# Graph server configuration
def get_graph_server_url() -> str:
    """Get graph server URL from config or env"""
    return os.getenv("SLOP_GRAPH_SERVER") or config.get("graph_server", "https://slop.at")

GRAPH_TIMEOUT = httpx.Timeout(30.0, connect=5.0)

# --- Core Slop Tool ---

@mcp.tool()
async def post_slop(title: str, content: str, tags: list[str] = None) -> str:
    """
    Post a slop to Slopnet! This creates a markdown file, extracts entities,
    publishes to the knowledge graph, and pushes to GitHub.

    Args:
        title: Title for the slop
        content: Markdown content (the actual slop)
        tags: Optional list of tags (defaults to ["slop"])

    Returns:
        Success message with URLs
    """
    # Check if repo is set up
    success, message = repo_manager.ensure_repo_exists()
    if not success:
        return message

    # Generate unique slop ID
    slop_id = str(uuid.uuid4())
    filename = f"{slop_id[:8]}.md"

    # Get metadata
    tags = tags or ["slop"]
    timestamp = datetime.datetime.now().isoformat()
    author = config.get("github_username", "unknown")

    # Build frontmatter
    frontmatter = (
        "---\n"
        f"title: {title}\n"
        f"author: {author}\n"
        f"created: {timestamp}\n"
        f"tags: [{', '.join(tags)}]\n"
        f"slop_id: {slop_id}\n"
        "---\n\n"
    )

    full_content = frontmatter + content

    # Save file to repo
    repo_path = config.get_repo_path()
    file_path = repo_path / filename

    try:
        file_path.write_text(full_content, encoding="utf-8")
    except Exception as e:
        return f"❌ Failed to write slop file: {e}"

    # Git commit & push
    commit_message = f"slop: {title}"
    success, git_msg = repo_manager.commit_and_push(file_path, commit_message)
    if not success:
        return f"❌ Git operation failed: {git_msg}"

    # Get GitHub URL
    github_url = repo_manager.get_file_github_url(file_path)
    if not github_url:
        github_url = f"https://github.com/{config.get('github_repo')}/blob/main/{filename}"

    # Extract entities using GLiNER2
    try:
        entities = extract_entities(full_content, threshold=0.5)
    except Exception as e:
        return f"⚠️ Slop posted but extraction failed: {e}\n{git_msg}\n📄 {github_url}"

    # Build RDF graph
    metadata = {
        "title": title,
        "author": author,
        "created": timestamp,
        "tags": tags,
        "slop_id": slop_id
    }

    try:
        graph = build_rdf_graph(file_path, github_url, entities, metadata)
        ntriples = graph_to_ntriples(graph)
    except Exception as e:
        return f"⚠️ Slop posted but RDF building failed: {e}\n{git_msg}\n📄 {github_url}"

    # Post to graph server
    graph_server = get_graph_server_url()
    insert_query = f"INSERT DATA {{\n{ntriples}\n}}"

    async with httpx.AsyncClient(timeout=GRAPH_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{graph_server}/update",
                content=insert_query,
                headers={"Content-Type": "application/sparql-update"}
            )
            response.raise_for_status()
        except Exception as e:
            return f"⚠️ Slop posted but graph update failed: {e}\n{git_msg}\n📄 {github_url}"

    # Success!
    return (
        f"🎉 Slop posted successfully!\n\n"
        f"📄 File: {github_url}\n"
        f"🧠 Extracted {len(entities)} entities\n"
        f"🌐 Published to {graph_server}\n"
        f"🆔 Slop ID: {slop_id[:8]}"
    )


# --- Setup & Configuration Tools ---

@mcp.tool()
def setup_slop_repo(github_repo: str) -> str:
    """
    Set up your slop repository for the first time.

    Args:
        github_repo: Your GitHub repo in format "username/repo-name"

    Example:
        setup_slop_repo("goodlux/slop")
    """
    return repo_manager.clone_repo(github_repo)[1]


@mcp.tool()
def check_slop_status() -> str:
    """Check if your slop repo is configured and ready."""
    success, message = repo_manager.ensure_repo_exists()

    if success:
        # Add config info
        graph_server = get_graph_server_url()
        author = config.get("github_username", "unknown")
        message += f"\n\n📊 Graph Server: {graph_server}\n✍️ Author: {author}"

    return message


# --- Query Tools ---

@mcp.tool()
async def query_slops(sparql_query: str) -> str:
    """
    Query the Slopnet knowledge graph with SPARQL.

    Examples:
    - "What has Izzy posted lately?"
    - "Who's writing about AI?"
    - "Show me slops about knowledge graphs"

    Args:
        sparql_query: SPARQL SELECT query

    Returns:
        Query results as JSON
    """
    graph_server = get_graph_server_url()
    url = f"{graph_server}/query"
    headers = {
        "Content-Type": "application/sparql-query",
        "Accept": "application/sparql-results+json"
    }

    async with httpx.AsyncClient(timeout=GRAPH_TIMEOUT) as client:
        try:
            response = await client.post(url, content=sparql_query, headers=headers)
            response.raise_for_status()
            results = response.json().get("results", {}).get("bindings", [])

            if not results:
                return "No results found."

            return str(results)
        except Exception as e:
            return f"❌ Query failed: {str(e)}"


@mcp.tool()
async def update_graph(sparql_update: str) -> str:
    """
    Execute a SPARQL UPDATE operation on the graph.
    Advanced users only - use with caution!

    Args:
        sparql_update: SPARQL UPDATE query (INSERT/DELETE)
    """
    graph_server = get_graph_server_url()
    url = f"{graph_server}/update"
    headers = {"Content-Type": "application/sparql-update"}

    async with httpx.AsyncClient(timeout=GRAPH_TIMEOUT) as client:
        try:
            response = await client.post(url, content=sparql_update, headers=headers)
            response.raise_for_status()
            return "✅ Graph updated successfully."
        except Exception as e:
            return f"❌ Update failed: {str(e)}"


# --- CRUD Tools ---

@mcp.tool()
def list_my_slops() -> str:
    """List all your slops in the local repo."""
    repo_path = config.get_repo_path()
    if not repo_path or not repo_path.exists():
        return "❌ No repo configured. Run setup_slop_repo() first."

    slops = list(repo_path.glob("*.md"))
    if not slops:
        return "No slops found. Post your first one with post_slop()!"

    slop_list = []
    for slop in sorted(slops, key=lambda p: p.stat().st_mtime, reverse=True):
        # Read frontmatter for title
        try:
            content = slop.read_text(encoding="utf-8")
            # Quick & dirty frontmatter parse
            if content.startswith("---"):
                fm_end = content.find("---", 3)
                if fm_end > 0:
                    fm = content[3:fm_end]
                    for line in fm.split("\n"):
                        if line.startswith("title:"):
                            title = line.split(":", 1)[1].strip()
                            slop_list.append(f"- {slop.name}: {title}")
                            break
        except:
            slop_list.append(f"- {slop.name}")

    return "📚 Your slops:\n" + "\n".join(slop_list)


def main():
    """Entry point for the mcp-slop CLI tool"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
