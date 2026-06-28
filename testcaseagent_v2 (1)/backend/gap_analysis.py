"""
gap_analysis.py - Analyzes documents for gaps and generates up to 10 clarifying questions.
"""

import json
import logging
from openai import OpenAI
from prompts import GAP_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


def _safe_json(text: str) -> dict | None:
    text = text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    try:
        return json.loads(text)
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        return None


def analyze_gaps(api_key: str, combined_content: str) -> dict:
    client = OpenAI(api_key=api_key)
    prompt = GAP_ANALYSIS_PROMPT.format(content=combined_content[:12000])
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, max_tokens=2000,
            response_format={"type": "json_object"},
        )
        parsed = _safe_json(resp.choices[0].message.content)
        if not parsed:
            return _fallback()
        questions = parsed.get("questions", [])[:10]
        for i, q in enumerate(questions, 1):
            q["id"] = i
        return {
            "gaps_found": parsed.get("gaps_found", []),
            "questions": questions,
            "doc_summary": parsed.get("doc_summary", ""),
            "question_count": len(questions),
        }
    except Exception as e:
        logger.error(f"Gap analysis failed: {e}")
        return _fallback()


def _fallback() -> dict:
    return {"gaps_found": [], "questions": [], "doc_summary": "Document analyzed.", "question_count": 0}


def format_qa_context(questions: list[dict], answers: dict[str, str]) -> str:
    if not answers:
        return "No additional context provided."
    lines = ["=== USER-PROVIDED CLARIFICATIONS ===\n"]
    for q in questions:
        qid = str(q["id"])
        answer = answers.get(qid, "").strip()
        if answer:
            lines.append(f"Q{qid} [{q['category']}]: {q['question']}")
            lines.append(f"Answer: {answer}\n")
    return "\n".join(lines) if len(lines) > 1 else "No additional context provided."
