import subprocess
import json
import time

def send_request(proc, method, params=None, request_id=1):
    """Sends a JSON-RPC request to the MCP server."""
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params or {}
    }
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()
    
    # Read response line by line until we get a valid JSON-RPC response
    line = proc.stdout.readline()
    if not line:
        return None
    return json.loads(line)

def test_everything():
    print("🚀 Starting MCP Server Test...")
    
    # Start the server process
    proc = subprocess.Popen(
        ["python", "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    try:
        # 1. THE HANDSHAKE (Initialize)
        print("\n[1/3] Initializing Handshake...")
        init_res = send_request(proc, "initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }, request_id=1)
        
        if init_res and "result" in init_res:
            print("✅ Initialization Successful.")
            # Send the mandatory 'initialized' notification
            proc.stdin.write(json.dumps({
                "jsonrpc": "2.0", 
                "method": "notifications/initialized"
            }) + "\n")
            proc.stdin.flush()
        else:
            print(f"❌ Initialization Failed: {init_res}")
            return

        # 2. LIST TOOLS
        print("\n[2/3] Fetching Available Tools...")
        tools_res = send_request(proc, "tools/list", request_id=2)
        if "result" in tools_res:
            tools = [t['name'] for t in tools_res['result']['tools']]
            print(f"✅ Tools Found: {tools}")
        else:
            print("❌ Failed to list tools.")

        # 3. SPARQL QUERY TEST (The 'Ping')
        print("\n[3/3] Testing SPARQL Query (Oxigraph Connection)...")
        query_params = {
            "name": "query_graph",
            "arguments": {
                "sparql_query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 1"
            }
        }
        
        query_res = send_request(proc, "tools/call", query_params, request_id=3)
        
        if "error" in query_res:
            print(f"❌ SPARQL Error: {query_res['error']['message']}")
        else:
            content = query_res["result"]["content"][0]["text"]
            print(f"✅ Database Response: {content}")
            print("\n🎉 ALL TESTS PASSED! Your MCP server and Axon store are communicating.")

    except Exception as e:
        print(f"💥 Script Error: {e}")
    finally:
        print("\nShutting down server...")
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_everything()