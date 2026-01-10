import pytest
import respx
from httpx import Response
from server import query_graph, update_graph

@pytest.mark.asyncio
@respx.mock
async def test_query_graph_success():
    # Mock the Axon Server response
    sparql_query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
    mock_data = {
        "results": {
            "bindings": [
                {"s": {"value": "http://example.com/s"}, "p": {"value": "http://example.com/p"}, "o": {"value": "http://example.com/o"}}
            ]
        }
    }
    
    respx.post("http://localhost:7878/query").mock(return_value=Response(200, json=mock_data))

    # Execute the tool
    result = await query_graph(sparql_query)
    
    assert "http://example.com/s" in result
    assert "bindings" not in result  # Ensures our formatting logic worked

@pytest.mark.asyncio
@respx.mock
async def test_update_graph_success():
    # Mock the Axon Server update endpoint
    sparql_update = "INSERT DATA { <http://s> <http://p> <http://o> }"
    respx.post("http://localhost:7878/update").mock(return_value=Response(200, text="Update successful"))

    result = await update_graph(sparql_update)
    
    assert result == "Update successful."
