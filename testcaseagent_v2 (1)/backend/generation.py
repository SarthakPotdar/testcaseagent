"""
generation.py - Generates test cases from knowledge graph + Q&A context.
"""

import json
import logging
from openai import OpenAI
from prompts import GENERATE_TESTCASES_PROMPT

logger = logging.getLogger(__name__)


def _parse_array(text):
    text = text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    try:
        p = json.loads(text)
        if isinstance(p, list):
            return p
        if isinstance(p, dict):
            for v in p.values():
                if isinstance(v, list):
                    return v
    except Exception as e:
        logger.error(f"Parse error: {e}")
    return None


def _validate(tc, idx):
    defaults = {
        "test_id": f"TC_{str(idx).zfill(3)}", "module": "General",
        "title": "Untitled Test Case", "description": "",
        "preconditions": "None", "test_steps": "1. Execute the test",
        "expected_result": "System behaves as expected",
        "priority": "Medium", "test_type": "Functional", "user_role": "User",
    }
    for k, v in defaults.items():
        if not tc.get(k):
            tc[k] = v
    if tc["priority"] not in ("High", "Medium", "Low"):
        tc["priority"] = "Medium"
    return tc


def generate_test_cases(api_key: str, knowledge_graph: dict, qa_context: str = "") -> list[dict]:
    client = OpenAI(api_key=api_key)
    graph_str = json.dumps(knowledge_graph, indent=2)
    if len(graph_str) > 14000:
        trimmed = {k: v[:20] for k, v in knowledge_graph.items()}
        graph_str = json.dumps(trimmed, indent=2)

    prompt = GENERATE_TESTCASES_PROMPT.format(
        knowledge_graph=graph_str,
        qa_context=qa_context or "No additional context provided.",
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4, max_tokens=4000,
    )
    tcs = _parse_array(resp.choices[0].message.content)
    if not tcs:
        raise ValueError("Could not parse test cases from AI response.")
    validated = [_validate(tc, i) for i, tc in enumerate(tcs, 1)]
    for i, tc in enumerate(validated, 1):
        tc["test_id"] = f"TC_{str(i).zfill(3)}"
    logger.info(f"Generated {len(validated)} test cases.")
    return validated


def get_summary(test_cases: list[dict]) -> dict:
    from collections import Counter
    return {
        "total": len(test_cases),
        "by_priority": dict(Counter(tc["priority"] for tc in test_cases)),
        "by_type": dict(Counter(tc["test_type"] for tc in test_cases)),
        "by_module": dict(Counter(tc["module"] for tc in test_cases)),
    }
