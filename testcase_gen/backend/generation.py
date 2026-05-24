"""
generation.py - Generates test cases from the knowledge graph using OpenAI.
"""

import json
import logging
from openai import OpenAI
from prompts import GENERATE_TESTCASES_PROMPT

logger = logging.getLogger(__name__)
MODEL = "gpt-4o-mini"


def _safe_parse_json_array(text: str) -> list | None:
    """Parse a JSON array response, stripping fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
        # Sometimes wrapped in a key
        if isinstance(parsed, dict):
            for val in parsed.values():
                if isinstance(val, list):
                    return val
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
    return None


def _validate_testcase(tc: dict, idx: int) -> dict:
    """Ensure all required fields are present with fallback defaults."""
    required = {
        "test_id": f"TC_{str(idx).zfill(3)}",
        "module": "General",
        "title": "Untitled Test Case",
        "description": "",
        "preconditions": "None",
        "test_steps": "1. Execute the test",
        "expected_result": "System behaves as expected",
        "priority": "Medium",
        "test_type": "Functional",
        "user_role": "User",
    }
    for key, default in required.items():
        if not tc.get(key):
            tc[key] = default
    # Normalize priority
    if tc["priority"] not in ("High", "Medium", "Low"):
        tc["priority"] = "Medium"
    return tc


def generate_test_cases(api_key: str, knowledge_graph: dict) -> list[dict]:
    """
    Generate test cases from a knowledge graph.

    Args:
        api_key: OpenAI API key
        knowledge_graph: dict from graph.build_knowledge_graph()["graph"]

    Returns:
        List of validated test case dicts.
    """
    client = OpenAI(api_key=api_key)

    graph_str = json.dumps(knowledge_graph, indent=2)

    # If graph is very large, trim lower-priority sections
    if len(graph_str) > 14000:
        trimmed = {
            "features": knowledge_graph.get("features", [])[:20],
            "user_roles": knowledge_graph.get("user_roles", [])[:10],
            "actions": knowledge_graph.get("actions", [])[:20],
            "business_rules": knowledge_graph.get("business_rules", [])[:15],
            "data_entities": knowledge_graph.get("data_entities", [])[:10],
            "edge_cases": knowledge_graph.get("edge_cases", [])[:15],
        }
        graph_str = json.dumps(trimmed, indent=2)
        logger.warning("Knowledge graph trimmed for token limit.")

    prompt = GENERATE_TESTCASES_PROMPT.format(knowledge_graph=graph_str)

    logger.info("Calling OpenAI to generate test cases...")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=4000,
    )

    raw = response.choices[0].message.content
    test_cases = _safe_parse_json_array(raw)

    if not test_cases:
        logger.error("Failed to parse test cases from LLM response.")
        raise ValueError("Could not parse test cases from AI response. Try again.")

    # Validate and normalize each test case
    validated = []
    for i, tc in enumerate(test_cases, 1):
        validated.append(_validate_testcase(tc, i))

    # Re-assign sequential IDs in case of duplicates
    for i, tc in enumerate(validated, 1):
        tc["test_id"] = f"TC_{str(i).zfill(3)}"

    logger.info(f"Generated {len(validated)} test cases.")
    return validated


def get_generation_summary(test_cases: list[dict]) -> dict:
    """Return summary statistics about generated test cases."""
    from collections import Counter

    priorities = Counter(tc["priority"] for tc in test_cases)
    test_types = Counter(tc["test_type"] for tc in test_cases)
    modules = Counter(tc["module"] for tc in test_cases)

    return {
        "total": len(test_cases),
        "by_priority": dict(priorities),
        "by_type": dict(test_types),
        "by_module": dict(modules),
    }
