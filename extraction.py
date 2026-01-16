"""
Entity extraction and RDF graph building for mcp-slop
Uses GLiNER2 with know.dev ontology
"""
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS
from gliner2 import GLiNER2


# Namespaces
KNOW = Namespace("https://know.dev/")
SCHEMA = Namespace("https://schema.org/")
NFO = Namespace("http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#")
SLOP = Namespace("https://slop.at/ontology#")

# Global model cache
_gliner_model = None


def get_gliner_model():
    """Lazy load GLiNER2 model"""
    global _gliner_model
    if _gliner_model is None:
        print("Loading GLiNER2 large model (340M params)...")
        _gliner_model = GLiNER2.from_pretrained("fastino/gliner2-large-v1")
        print("Model loaded!")
    return _gliner_model


def get_know_dev_schema() -> Dict[str, str]:
    """
    Return know.dev entity types for GLiNER2 extraction

    Based on know.dev ontology, focusing on types extractable from text
    """
    return {
        # Core entities
        "Person": "People mentioned by name",
        "Organization": "Companies, institutions, groups",
        "Place": "Locations, venues, cities, countries",
        "Event": "Meetings, conferences, activities, parties",

        # Activities
        "Meeting": "Scheduled meetings or gatherings",
        "Activity": "Actions or activities performed",
        "Conference": "Professional conferences or symposiums",

        # Concepts
        "DefinedTerm": "Technical terms, concepts, or keywords",
        "Topic": "Subjects or topics discussed",

        # Social structures
        "Family": "Family units or groups",
        "Community": "Communities or social groups",
        "Company": "Business entities or companies",
    }


def get_know_dev_relations() -> Dict[str, str]:
    """
    Return know.dev relationship types for GLiNER2 relation extraction

    Start simple - can expand later
    """
    return {
        "knows": "Person knows another person",
        "colleague": "Professional relationship between people",
        "worksFor": "Person works for an organization",
        "attendedEvent": "Person attended an event",
        "locatedIn": "Entity located in a place",
    }


def extract_entities(text: str, threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Extract entities from text using GLiNER2 and know.dev schema

    Args:
        text: Text to extract entities from
        threshold: Confidence threshold (0.0-1.0)

    Returns:
        List of entities with text, label, position, and confidence
    """
    model = get_gliner_model()
    schema = get_know_dev_schema()

    # Extract entities
    results = model.extract_entities(
        text,
        schema,
        include_confidence=True,
        include_spans=True,
        threshold=threshold
    )

    entities = []

    if isinstance(results, dict) and 'entities' in results:
        for label, entity_list in results['entities'].items():
            if isinstance(entity_list, list):
                for entity in entity_list:
                    if isinstance(entity, dict):
                        start_char = entity.get("start", 0)
                        end_char = entity.get("end", 0)
                        entities.append({
                            "text": entity.get("text", ""),
                            "label": label,
                            "start": start_char,
                            "end": end_char,
                            "line_start": char_to_line(text, start_char),
                            "line_end": char_to_line(text, end_char),
                            "score": entity.get("confidence", entity.get("score", 0.0))
                        })

    return entities


def char_to_line(text: str, char_pos: int) -> int:
    """Convert character position to line number (1-indexed)"""
    if char_pos < 0:
        return 1
    if char_pos >= len(text):
        return text.count('\n') + 1
    return text[:char_pos].count('\n') + 1


def create_entity_uri(text: str) -> str:
    """Create a stable URI for an entity based on its text"""
    normalized = text.lower().strip()
    hash_val = hashlib.md5(normalized.encode()).hexdigest()[:8]
    slug = normalized.replace(' ', '-')[:50]  # Limit slug length
    return f"https://slop.at/entity/{hash_val}/{slug}"


def create_file_uri(github_repo: str, filename: str, commit_hash: str = "main") -> str:
    """Create a URI for a slop file"""
    return f"https://github.com/{github_repo}/blob/{commit_hash}/{filename}"


def build_rdf_graph(
    filepath: Path,
    github_url: str,
    entities: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> Graph:
    """
    Build RDF graph with slop metadata and extracted entities

    Args:
        filepath: Local path to the slop file
        github_url: Public GitHub URL for the file
        entities: Extracted entities from GLiNER2
        metadata: Frontmatter metadata (title, author, tags, etc)

    Returns:
        RDF Graph ready for serialization
    """
    g = Graph()

    # Bind namespaces
    g.bind("know", KNOW)
    g.bind("schema", SCHEMA)
    g.bind("nfo", NFO)
    g.bind("slop", SLOP)
    g.bind("dcterms", DCTERMS)

    # File URI
    file_uri = URIRef(github_url)

    # File metadata
    g.add((file_uri, RDF.type, NFO.FileDataObject))
    g.add((file_uri, RDF.type, SLOP.Slop))
    g.add((file_uri, NFO.fileName, Literal(filepath.name)))
    g.add((file_uri, NFO.fileUrl, URIRef(github_url)))

    # Frontmatter metadata
    if "title" in metadata:
        g.add((file_uri, DCTERMS.title, Literal(metadata["title"])))
    if "author" in metadata:
        g.add((file_uri, DCTERMS.creator, Literal(metadata["author"])))
    if "created" in metadata:
        g.add((file_uri, DCTERMS.created, Literal(metadata["created"])))
    if "tags" in metadata and isinstance(metadata["tags"], list):
        for tag in metadata["tags"]:
            g.add((file_uri, DCTERMS.subject, Literal(tag)))
    if "slop_id" in metadata:
        g.add((file_uri, SLOP.slopId, Literal(metadata["slop_id"])))

    # Extract entities and add to graph
    for entity in entities:
        entity_uri = URIRef(create_entity_uri(entity["text"]))

        # Use know.dev class for entity type
        entity_type = KNOW[entity["label"]]

        # Base triples
        g.add((entity_uri, RDF.type, entity_type))
        g.add((entity_uri, SCHEMA.name, Literal(entity["text"])))

        # Link entity to slop
        g.add((file_uri, SLOP.mentions, entity_uri))

        # Provenance using blank nodes
        provenance = BNode()
        g.add((provenance, SLOP.subject, entity_uri))
        g.add((provenance, SLOP.predicate, SCHEMA.name))
        g.add((provenance, SLOP.object, Literal(entity["text"])))
        g.add((provenance, SLOP.extractedFrom, file_uri))
        g.add((provenance, SLOP.confidence, Literal(entity["score"], datatype=XSD.float)))

        # Add line numbers for source linking
        if "line_start" in entity:
            g.add((provenance, SLOP.lineStart, Literal(entity["line_start"], datatype=XSD.integer)))
        if "line_end" in entity:
            g.add((provenance, SLOP.lineEnd, Literal(entity["line_end"], datatype=XSD.integer)))

        # Create entity-specific GitHub URL with line anchor
        if "line_start" in entity and "line_end" in entity:
            line_start = entity["line_start"]
            line_end = entity["line_end"]
            if line_start == line_end:
                entity_url = f"{github_url}#L{line_start}"
            else:
                entity_url = f"{github_url}#L{line_start}-L{line_end}"
            g.add((provenance, SLOP.sourceUrl, URIRef(entity_url)))

    return g


def graph_to_ntriples(graph: Graph) -> str:
    """Serialize RDF graph to N-Triples format"""
    return graph.serialize(format="nt")
