import os
import httpx
from mcp.server.fastmcp import FastMCP
from pathlib import Path

# Initialize FastMCP
mcp = FastMCP("AxonBridge")

# Axon Server Configuration
AXON_HOST = os.getenv("AXON_HOST", "localhost")
AXON_PORT = os.getenv("AXON_PORT", "7878")
BASE_URL = f"http://{AXON_HOST}:{AXON_PORT}"

# Define a standard timeout for all Axon requests
# connect: time to establish socket; read: time to wait for data chunk
AXON_TIMEOUT = httpx.Timeout(30.0, connect=5.0)

@mcp.tool()
def check_axon_repo() -> str:
    """Check if the hidden Axon repository folder exists on the local machine."""
    # Define the hidden path in the user's home directory
    home = Path.home()
    repo_path = home / ".axon-repo"
    
    if repo_path.exists():
        return f"✅ Found Axon repository at: {repo_path}"
    else:
        return (
            "❌ Hidden Axon repository NOT found.\n\n"
            "To create it, please run these commands in your terminal:\n"
            f"1. mkdir '{repo_path}'\n"
            f"2. attrib +h '{repo_path}'  (This hides the folder on Windows)"
        )
async def query_graph(sparql_query: str) -> str:
    """Execute a SPARQL SELECT query against the remote Axon Server."""
    url = f"{BASE_URL}/query"
    headers = {
        "Content-Type": "application/sparql-query",
        "Accept": "application/sparql-results+json"
    }
    
    async with httpx.AsyncClient(timeout=AXON_TIMEOUT) as client:
        try:
            response = await client.post(url, content=sparql_query, headers=headers)
            response.raise_for_status()
            results = response.json().get("results", {}).get("bindings", [])
            return str(results)
        except httpx.TimeoutException:
            return "Error: The query to Axon Server timed out. Try a more specific query or adding a LIMIT."
        except httpx.HTTPStatusError as e:
            return f"Error: Axon Server returned a status error ({e.response.status_code})."
        except Exception as e:
            return f"Error querying Axon Server: {str(e)}"

@mcp.tool()
async def update_graph(sparql_update: str) -> str:
    """Execute a SPARQL UPDATE operation on the remote Axon Server."""
    url = f"{BASE_URL}/update"
    headers = {"Content-Type": "application/sparql-update"}
    
    async with httpx.AsyncClient(timeout=AXON_TIMEOUT) as client:
        try:
            response = await client.post(url, content=sparql_update, headers=headers)
            response.raise_for_status()
            return "Update successful."
        except httpx.TimeoutException:
            return "Error: The update request timed out."
        except Exception as e:
            return f"Error updating Axon Server: {str(e)}"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
