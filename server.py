import os
from mcp.server.fastmcp import FastMCP
import pyoxigraph

# Initialize FastMCP
mcp = FastMCP("AxonServer")

# Configuration from environment or defaults
DATA_DIR = os.getenv("AXON_DATA_DIR", "./data")
store = pyoxigraph.Store(DATA_DIR)

@mcp.tool()
def query_graph(sparql_query: str) -> str:
    """Execute a SPARQL SELECT query against the Axon store."""
    try:
        results = store.query(sparql_query)
        output = []
        for solution in results:
            output.append({str(k): str(v) for k, v in solution.items()})
        return str(output)
    except Exception as e:
        return f"Error executing query: {str(e)}"

@mcp.tool()
def update_graph(sparql_update: str) -> str:
    """Execute a SPARQL UPDATE (INSERT/DELETE) operation."""
    try:
        store.update(sparql_update)
        return "Update successful."
    except Exception as e:
        return f"Error updating graph: {str(e)}"

@mcp.resource("axon://schema")
def get_schema_info() -> str:
    """Returns the primary vocabularies used in this Axon instance."""
    return "This server primarily uses Schema.org vocabularies for data extraction."

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
