import os
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("AxonBridge")

# Axon Server Configuration
AXON_HOST = os.getenv("AXON_HOST", "localhost")
AXON_PORT = os.getenv("AXON_PORT", "7878")
BASE_URL = f"http://{AXON_HOST}:{AXON_PORT}"

@mcp.tool()
async def query_graph(sparql_query: str) -> str:
    """Execute a SPARQL SELECT query against the remote Axon Server."""
    url = f"{BASE_URL}/query"
    headers = {
        "Content-Type": "application/sparql-query",
        "Accept": "application/sparql-results+json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, content=sparql_query, headers=headers)
            response.raise_for_status()
            return str(response.json().get("results", {}).get("bindings", []))
        except Exception as e:
            return f"Error querying Axon Server: {str(e)}"

@mcp.tool()
async def update_graph(sparql_update: str) -> str:
    """Execute a SPARQL UPDATE operation on the remote Axon Server."""
    url = f"{BASE_URL}/update"
    headers = {"Content-Type": "application/sparql-update"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, content=sparql_update, headers=headers)
            response.raise_for_status()
            return "Update successful."
        except Exception as e:
            return f"Error updating Axon Server: {str(e)}"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
