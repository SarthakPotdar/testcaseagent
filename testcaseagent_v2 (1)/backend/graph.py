"""
graph.py - Knowledge graph builder using OpenAI.
"""

import json
import logging
from openai import OpenAI
from prompts import EXTRACT_ENTITIES_PROMPT, MERGE_GRAPHS_PROMPT, SUMMARIZE_DOCUMENT_PROMPT

logger = logging.getLogger(__name__)
MODEL = "gpt-4o-mini"
MAX_CHUNK = 12000


def _chunk(text: str) -> list[str]:
    if len(text) <= MAX_CHUNK:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        end = start + MAX_CHUNK
        if end < len(text):
            bp = text.rfind("\n", start, end)
            if bp > start:
                end = bp
        chunks.append(text[start:end])
        start = end - 500
    return chunks


def _call_json(client, prompt):
    r = client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}],
        temperature=0.1, response_format={"type": "json_object"})
    return r.choices[0].message.content


def _call_text(client, prompt):
    r = client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.3)
    return r.choices[0].message.content


def _parse(text):
    text = text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    try:
        return json.loads(text)
    except Exception:
        return None


def _empty():
    return {"features": [], "user_roles": [], "actions": [], "business_rules": [], "data_entities": [], "edge_cases": []}


def _structural_merge(graphs):
    merged, seen = _empty(), {k: set() for k in _empty()}
    def dedup(key, items, nf):
        for item in items:
            n = item.get(nf, "").lower().strip()
            if n and n not in seen[key]:
                seen[key].add(n)
                merged[key].append(item)
    for g in graphs:
        dedup("features", g.get("features", []), "name")
        dedup("user_roles", g.get("user_roles", []), "role")
        dedup("actions", g.get("actions", []), "action")
        dedup("business_rules", g.get("business_rules", []), "rule")
        dedup("data_entities", g.get("data_entities", []), "entity")
        dedup("edge_cases", g.get("edge_cases", []), "scenario")
    return merged


def _merge(client, graphs):
    gs = json.dumps(graphs, indent=2)
    if len(gs) > 15000:
        return _structural_merge(graphs)
    try:
        raw = _call_json(client, MERGE_GRAPHS_PROMPT.format(graphs=gs))
        parsed = _parse(raw)
        return parsed if parsed else _structural_merge(graphs)
    except Exception:
        return _structural_merge(graphs)


def build_knowledge_graph(api_key: str, docs: list[dict], qa_context: str = "") -> dict:
    client = OpenAI(api_key=api_key)
    successful = [d for d in docs if d.get("status") == "success" and d.get("content")]
    if not successful:
        raise ValueError("No successfully ingested documents to process.")

    doc_graphs, summaries = {}, {}
    for doc in successful:
        fname = doc["filename"]
        chunks = _chunk(doc["content"])
        chunk_graphs = []
        for i, chunk in enumerate(chunks):
            logger.info(f"  chunk {i+1}/{len(chunks)} of '{fname}'")
            try:
                raw = _call_json(client, EXTRACT_ENTITIES_PROMPT.format(content=chunk, qa_context=qa_context))
                p = _parse(raw)
                if p:
                    chunk_graphs.append(p)
            except Exception as e:
                logger.error(f"chunk error: {e}")
        doc_graphs[fname] = chunk_graphs[0] if len(chunk_graphs) == 1 else (_merge(client, chunk_graphs) if chunk_graphs else _empty())
        try:
            summaries[fname] = _call_text(client, SUMMARIZE_DOCUMENT_PROMPT.format(content=doc["content"][:3000]))
        except Exception:
            summaries[fname] = "Summary unavailable."

    all_graphs = list(doc_graphs.values())
    final = all_graphs[0] if len(all_graphs) == 1 else _merge(client, all_graphs)

    stats = {
        "documents_processed": len(successful),
        "features_found": len(final.get("features", [])),
        "user_roles_found": len(final.get("user_roles", [])),
        "actions_found": len(final.get("actions", [])),
        "business_rules_found": len(final.get("business_rules", [])),
        "data_entities_found": len(final.get("data_entities", [])),
        "edge_cases_found": len(final.get("edge_cases", [])),
    }
    return {"graph": final, "summaries": summaries, "stats": stats}
