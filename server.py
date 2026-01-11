import os
import subprocess
import httpx
import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("AxonBridge")

# --- Configurations ---
AXON_HOST = os.getenv("AXON_HOST", "localhost")
AXON_PORT = os.getenv("AXON_PORT", "7878")
BASE_URL = f"http://{AXON_HOST}:{AXON_PORT}"
AXON_TIMEOUT = httpx.Timeout(30.0, connect=5.0)
REPO_ROOT = Path.home() / ".axon-repo"

# --- Axon Graph Tools ---
@mcp.tool()
def init_axon_repo(remote_url: str = None) -> str:
    """
    Programmatically initializes the .axon-repo as a Git repository.
    Sets the branch to 'main' and adds a remote origin if a URL is provided.
    """
    repo_path = str(REPO_ROOT)
    git_dir = REPO_ROOT / ".git"
    
    steps = []
    try:
        # 1. Initialize Git if .git doesn't exist
        if not git_dir.exists():
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True)
            steps.append("✅ Git initialized and branch set to 'main'.")
        else:
            steps.append("ℹ️ Git is already initialized.")

        # 2. Add remote origin if provided
        if remote_url:
            # Check if remote exists
            remotes = subprocess.run(["git", "remote"], cwd=repo_path, capture_output=True, text=True).stdout
            if "origin" in remotes:
                subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=repo_path, check=True)
                steps.append(f"✅ Updated remote origin to {remote_url}")
            else:
                subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=repo_path, check=True)
                steps.append(f"✅ Added remote origin: {remote_url}")
        
        return "\n".join(steps)
    except Exception as e:
        return f"❌ Initialization failed: {str(e)}"
        
@mcp.tool()
def create_slop(title: str, content: str, tags: list[str] = None) -> str:
    """
    Creates a 'Slop' file: Markdown with frontmatter for Obsidian/Axon indexing.
    Saves to the hidden .axon-repo for synchronization.
    """
    tags = tags or ["slop", "axon-bridge"]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Generate the Slop Frontmatter
    frontmatter = (
        "---\n"
        f"title: {title}\n"
        f"created: {timestamp}\n"
        f"tags: [{', '.join(tags)}]\n"
        "type: slop\n"
        "---\n\n"
    )
    
    filename = f"{title.lower().replace(' ', '_')}.md"
    full_content = frontmatter + content
    
    return write_axon_file(filename, full_content)
    
@mcp.tool()
def git_push(remote: str = "origin", branch: str = "main", repo_path: str = ".") -> str:
    """
    Pushes committed changes to a remote GitHub repository.
    Crucial for the 'Slopnet' architecture to share knowledge.
    """
    try:
        subprocess.run(
            ["git", "push", remote, branch],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        return f"🚀 Successfully pushed to {remote}/{branch}"
    except subprocess.CalledProcessError as e:
        return f"❌ Push failed: {e.stderr}"

@mcp.tool()
async def query_graph(sparql_query: str) -> str:
    """Execute a SPARQL SELECT query against the remote Axon Server."""
    url = f"{BASE_URL}/query"
    headers = {"Content-Type": "application/sparql-query", "Accept": "application/sparql-results+json"}
    async with httpx.AsyncClient(timeout=AXON_TIMEOUT) as client:
        try:
            response = await client.post(url, content=sparql_query, headers=headers)
            response.raise_for_status()
            return str(response.json().get("results", {}).get("bindings", []))
        except Exception as e:
            return f"❌ Error querying Axon: {str(e)}"

@mcp.tool()
async def update_graph(sparql_update: str) -> str:
    """Execute a SPARQL UPDATE (INSERT/DELETE) operation on the Axon Server."""
    url = f"{BASE_URL}/update"
    headers = {"Content-Type": "application/sparql-update"}
    async with httpx.AsyncClient(timeout=AXON_TIMEOUT) as client:
        try:
            response = await client.post(url, content=sparql_update, headers=headers)
            response.raise_for_status()
            return "✅ Update successful."
        except Exception as e:
            return f"❌ Error updating Axon: {str(e)}"

# --- Local File & Repo Management Tools ---

@mcp.tool()
def check_axon_repo() -> str:
    """Check for the hidden Axon repository and list its contents."""
    if not REPO_ROOT.exists():
        return (
            "❌ Hidden Axon repository NOT found.\n"
            f"Run in PowerShell: mkdir '{REPO_ROOT}'; attrib +h '{REPO_ROOT}'"
        )
    files = [f.name for f in REPO_ROOT.iterdir()]
    content_str = "\n".join([f"- {f}" for f in files]) if files else "Empty"
    return f"✅ Found Axon repo at {REPO_ROOT}\nContents:\n{content_str}"

@mcp.tool()
def read_axon_file(filename: str) -> str:
    """Read a specific file from the hidden .axon-repo."""
    file_path = REPO_ROOT / filename
    if not file_path.is_file(): return "❌ File not found."
    try:
        return f"📄 Content of {filename}:\n\n{file_path.read_text(encoding='utf-8')}"
    except Exception as e: return f"❌ Read error: {str(e)}"

@mcp.tool()
def write_axon_file(filename: str, content: str) -> str:
    """Write or update a file in the hidden .axon-repo."""
    REPO_ROOT.mkdir(exist_ok=True)
    file_path = REPO_ROOT / filename
    try:
        file_path.write_text(content, encoding="utf-8")
        return f"✅ Successfully wrote to {filename}"
    except Exception as e: return f"❌ Write error: {str(e)}"

# --- Git Workflow Tools ---

@mcp.tool()
def get_git_status(repo_path: str = ".") -> str:
    """Runs 'git status' to see modified and staged files."""
    try:
        res = subprocess.run(["git", "status"], cwd=repo_path, capture_output=True, text=True, check=True)
        return res.stdout
    except Exception as e: return f"❌ Git Error: {str(e)}"

@mcp.tool()
def get_staged_diff(repo_path: str = ".") -> str:
    """Gets the diff of staged changes for the AI to summarize."""
    try:
        res = subprocess.run(["git", "diff", "--staged"], cwd=repo_path, capture_output=True, text=True, check=True)
        return res.stdout or "No changes staged."
    except Exception as e: return f"❌ Diff Error: {str(e)}"

@mcp.tool()
def create_branch(branch_name: str, repo_path: str = ".") -> str:
    """Creates and switches to a new git branch."""
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_path, check=True, capture_output=True)
        return f"✅ Switched to new branch: {branch_name}"
    except Exception as e: return f"❌ Branch Error: {str(e)}"

@mcp.tool()
def git_commit(message: str, repo_path: str = ".") -> str:
    """Commits staged changes with a message."""
    try:
        subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True, capture_output=True)
        return f"✅ Committed: {message}"
    except Exception as e: return f"❌ Commit Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
