"""
Entity extraction and RDF graph building for mcp-slop
Uses GLiNER2 with know.dev ontology and pyoxigraph for RDF-star support
"""
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from pyoxigraph import NamedNode, Literal, Quad
from gliner2 import GLiNER2


# Namespace URIs
KNOW = "https://know.dev/"
SCHEMA = "https://schema.org/"
NFO = "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#"
SLOP = "https://slop.at/ontology#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
DCTERMS = "http://purl.org/dc/terms/"
XSD = "http://www.w3.org/2001/XMLSchema#"

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
) -> tuple[List[Quad], str]:
    """
    Build RDF graph with slop metadata and extracted entities using RDF-star

    Args:
        filepath: Local path to the slop file
        github_url: Public GitHub URL for the file
        entities: Extracted entities from GLiNER2
        metadata: Frontmatter metadata (title, author, tags, etc)

    Returns:
        Tuple of (List of Quads with RDF-star support, graph URI string)
    """
    quads = []

    # File URI
    file_uri = NamedNode(github_url)

    # Generate graph URI: https://slop.at/graph/{user}/{repo}/{slop-id}
    slop_id = metadata.get("slop_id", "unknown")
    author = metadata.get("author", "unknown")
    # Extract repo from github_url (format: https://github.com/{user}/{repo}/blob/...)
    repo_name = github_url.split("/")[4] if len(github_url.split("/")) > 4 else "slop"
    graph_uri = f"https://slop.at/graph/{author}/{repo_name}/{slop_id}"
    graph_node = NamedNode(graph_uri)

    # Helper to add quad
    # Note: s can be NamedNode, BlankNode, or Triple (for RDF-star quoted triples)
    def add_quad(s, p, o):
        quads.append(Quad(s, p, o, graph_node))

    # File metadata
    add_quad(file_uri, NamedNode(f"{RDF}type"), NamedNode(f"{NFO}FileDataObject"))
    add_quad(file_uri, NamedNode(f"{RDF}type"), NamedNode(f"{SLOP}Slop"))
    add_quad(file_uri, NamedNode(f"{NFO}fileName"), Literal(filepath.name))
    add_quad(file_uri, NamedNode(f"{NFO}fileUrl"), NamedNode(github_url))

    # Frontmatter metadata
    if "title" in metadata:
        add_quad(file_uri, NamedNode(f"{DCTERMS}title"), Literal(metadata["title"]))
    if "author" in metadata:
        add_quad(file_uri, NamedNode(f"{DCTERMS}creator"), Literal(metadata["author"]))
    if "created" in metadata:
        add_quad(file_uri, NamedNode(f"{DCTERMS}created"), Literal(metadata["created"]))
    if "tags" in metadata and isinstance(metadata["tags"], list):
        for tag in metadata["tags"]:
            add_quad(file_uri, NamedNode(f"{DCTERMS}subject"), Literal(tag))
    if "slop_id" in metadata:
        add_quad(file_uri, NamedNode(f"{SLOP}slopId"), Literal(metadata["slop_id"]))
    if "familiar" in metadata:
        add_quad(file_uri, NamedNode(f"{SLOP}familiar"), Literal(metadata["familiar"]))

    # Extract entities and add to graph
    for entity in entities:
        entity_uri = NamedNode(create_entity_uri(entity["text"]))
        entity_type = NamedNode(f"{KNOW}{entity['label']}")

        # Entity triples
        add_quad(entity_uri, NamedNode(f"{RDF}type"), entity_type)
        add_quad(entity_uri, NamedNode(f"{SCHEMA}name"), Literal(entity["text"]))

        # Link entity to slop
        add_quad(file_uri, NamedNode(f"{SLOP}mentions"), entity_uri)

        # Extraction metadata (attached directly to entity)
        # The named graph already provides file-level provenance
        add_quad(entity_uri, NamedNode(f"{SLOP}confidence"),
                Literal(str(entity["score"]), datatype=NamedNode(f"{XSD}float")))

        # Add line numbers for source linking
        if "line_start" in entity:
            add_quad(entity_uri, NamedNode(f"{SLOP}lineStart"),
                    Literal(str(entity["line_start"]), datatype=NamedNode(f"{XSD}integer")))
        if "line_end" in entity:
            add_quad(entity_uri, NamedNode(f"{SLOP}lineEnd"),
                    Literal(str(entity["line_end"]), datatype=NamedNode(f"{XSD}integer")))

        # Create entity-specific GitHub URL with line anchor
        if "line_start" in entity and "line_end" in entity:
            line_start = entity["line_start"]
            line_end = entity["line_end"]
            if line_start == line_end:
                entity_url = f"{github_url}#L{line_start}"
            else:
                entity_url = f"{github_url}#L{line_start}-L{line_end}"
            add_quad(entity_uri, NamedNode(f"{SLOP}sourceUrl"), NamedNode(entity_url))

    return quads, graph_uri


def quads_to_sparql_insert(quads: List[Quad]) -> str:
    """Convert quads to SPARQL INSERT DATA with GRAPH clauses"""
    from collections import defaultdict

    # Group quads by graph
    graphs = defaultdict(list)
    for quad in quads:
        graph_uri = str(quad.graph_name) if quad.graph_name else None
        triple = f"{quad.subject.n3()} {quad.predicate.n3()} {quad.object.n3()} ."
        graphs[graph_uri].append(triple)

    # Build SPARQL INSERT DATA
    parts = ["INSERT DATA {"]

    for graph_uri, triples in graphs.items():
        if graph_uri:
            parts.append(f"  GRAPH <{graph_uri}> {{")
            for triple in triples:
                parts.append(f"    {triple}")
            parts.append("  }")
        else:
            # Default graph
            for triple in triples:
                parts.append(f"  {triple}")

    parts.append("}")
    return "\n".join(parts)
