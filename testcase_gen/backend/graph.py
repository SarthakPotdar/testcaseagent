"""
graph.py - Builds a knowledge graph from ingested document text using OpenAI.
Uses gpt-4o-mini for cost efficiency.
"""

import json
import logging
from openai import OpenAI
from prompts import EXTRACT_ENTITIES_PROMPT, MERGE_GRAPHS_PROMPT, SUMMARIZE_DOCUMENT_PROMPT

logger = logging.getLogger(__name__)

MODEL = "gpt-4o-mini"
MAX_CHUNK_CHARS = 12000  # Stay well within context limits


def _chunk_text(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split large text into overlapping chunks."""
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        # Try to break on a newline
        if end < len(text):
            break_point = text.rfind("\n", start, end)
            if break_point > start:
                end = break_point
        chunks.append(text[start:end])
        start = end - 500  # 500 char overlap
    return chunks


def _call_openai(client: OpenAI, prompt: str) -> str:
    """Make a single OpenAI chat completion call and return text response."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def _call_openai_text(client: OpenAI, prompt: str) -> str:
    """Make a plain text (non-JSON) OpenAI call."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content


def _safe_parse_json(text: str) -> dict | list | None:
    """Safely parse JSON, stripping markdown fences if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw text: {text[:500]}")
        return None


def extract_entities_from_document(client: OpenAI, content: str, filename: str) -> dict:
    """
    Extract structured entities from a single document's text.
    Handles chunking for large documents.
    """
    chunks = _chunk_text(content)
    chunk_graphs = []

    for i, chunk in enumerate(chunks):
        logger.info(f"  Processing chunk {i+1}/{len(chunks)} of '{filename}'...")
        prompt = EXTRACT_ENTITIES_PROMPT.format(content=chunk)
        try:
            raw = _call_openai(client, prompt)
            parsed = _safe_parse_json(raw)
            if parsed:
                chunk_graphs.append(parsed)
        except Exception as e:
            logger.error(f"  Error on chunk {i+1}: {e}")

    if not chunk_graphs:
        return _empty_graph()

    if len(chunk_graphs) == 1:
        return chunk_graphs[0]

    # Merge chunks from the same document
    return _merge_graphs(client, chunk_graphs)


def _merge_graphs(client: OpenAI, graphs: list[dict]) -> dict:
    """Merge multiple entity graphs into one using the LLM."""
    graphs_str = json.dumps(graphs, indent=2)

    # If payload is large, do a simple structural merge first
    if len(graphs_str) > 15000:
        merged = _structural_merge(graphs)
        return merged

    prompt = MERGE_GRAPHS_PROMPT.format(graphs=graphs_str)
    try:
        raw = _call_openai(client, prompt)
        parsed = _safe_parse_json(raw)
        if parsed:
            return parsed
    except Exception as e:
        logger.error(f"LLM merge failed: {e}, falling back to structural merge")

    return _structural_merge(graphs)


def _structural_merge(graphs: list[dict]) -> dict:
    """Simple deduplication-based merge without LLM."""
    merged = _empty_graph()
    seen = {key: set() for key in merged}

    def dedup_add(key: str, items: list, name_field: str):
        for item in items:
            name = item.get(name_field, "").lower().strip()
            if name and name not in seen[key]:
                seen[key].add(name)
                merged[key].append(item)

    for g in graphs:
        dedup_add("features", g.get("features", []), "name")
        dedup_add("user_roles", g.get("user_roles", []), "role")
        dedup_add("actions", g.get("actions", []), "action")
        dedup_add("business_rules", g.get("business_rules", []), "rule")
        dedup_add("data_entities", g.get("data_entities", []), "entity")
        dedup_add("edge_cases", g.get("edge_cases", []), "scenario")

    return merged


def _empty_graph() -> dict:
    return {
        "features": [],
        "user_roles": [],
        "actions": [],
        "business_rules": [],
        "data_entities": [],
        "edge_cases": [],
    }


def summarize_document(client: OpenAI, content: str) -> str:
    """Generate a brief summary of a document."""
    snippet = content[:3000]
    prompt = SUMMARIZE_DOCUMENT_PROMPT.format(content=snippet)
    try:
        return _call_openai_text(client, prompt)
    except Exception as e:
        logger.error(f"Summary failed: {e}")
        return "Summary unavailable."


def build_knowledge_graph(api_key: str, ingested_docs: list[dict]) -> dict:
    """
    Main entry point. Build a unified knowledge graph from all ingested documents.

    Args:
        api_key: OpenAI API key
        ingested_docs: list of dicts from ingestion.py with keys: filename, content, status

    Returns:
        {
            "graph": dict (the merged knowledge graph),
            "summaries": {filename: summary},
            "doc_graphs": {filename: individual graph},
            "stats": {...}
        }
    """
    client = OpenAI(api_key=api_key)

    successful_docs = [d for d in ingested_docs if d.get("status") == "success" and d.get("content")]
    if not successful_docs:
        raise ValueError("No successfully ingested documents to process.")

    doc_graphs = {}
    summaries = {}

    for doc in successful_docs:
        fname = doc["filename"]
        logger.info(f"Building graph for: {fname}")
        doc_graphs[fname] = extract_entities_from_document(client, doc["content"], fname)
        summaries[fname] = summarize_document(client, doc["content"])

    # Merge all document graphs
    all_graphs = list(doc_graphs.values())
    if len(all_graphs) == 1:
        final_graph = all_graphs[0]
    else:
        logger.info("Merging all document graphs...")
        final_graph = _merge_graphs(client, all_graphs)

    stats = {
        "documents_processed": len(successful_docs),
        "features_found": len(final_graph.get("features", [])),
        "user_roles_found": len(final_graph.get("user_roles", [])),
        "actions_found": len(final_graph.get("actions", [])),
        "business_rules_found": len(final_graph.get("business_rules", [])),
        "data_entities_found": len(final_graph.get("data_entities", [])),
        "edge_cases_found": len(final_graph.get("edge_cases", [])),
    }

    logger.info(f"Knowledge graph built: {stats}")

    return {
        "graph": final_graph,
        "summaries": summaries,
        "doc_graphs": doc_graphs,
        "stats": stats,
    }
