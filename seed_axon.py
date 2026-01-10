import pyoxigraph
import os

# Use the same data directory as your MCP server
DATA_DIR = os.getenv("AXON_DATA_DIR", "./data")
store = pyoxigraph.Store(DATA_DIR)

def seed_data():
    print(f"🌱 Seeding data into: {os.path.abspath(DATA_DIR)}")
    
    # We'll insert a SoftwareApplication (Axon) and an Author
    insert_query = """
    PREFIX schema: <https://schema.org/>
    INSERT DATA {
        <https://github.com/repolex-ai/axon-server> a schema:SoftwareApplication ;
            schema:name "Axon Server" ;
            schema:softwareVersion "2026.1.0" ;
            schema:applicationCategory "Knowledge Graph" ;
            schema:description "An MCP-native RDF metadata extractor and server." .
            
        <https://github.com/israel> a schema:Person ;
            schema:name "Israel" ;
            schema:jobTitle "Developer" .
    }
    """
    
    try:
        store.update(insert_query)
        print("✅ Data seeded successfully!")
        
        # Quick verification count
        results = store.query("SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }")
        for solution in results:
            print(f"📊 Total triples in store: {solution['count']}")
            
    except Exception as e:
        print(f"❌ Error seeding data: {e}")

if __name__ == "__main__":
    seed_data()