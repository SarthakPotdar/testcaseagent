"""
prompts.py - All LLM prompts for the Test Case Agent.
"""

GAP_ANALYSIS_PROMPT = """You are a senior QA analyst reviewing a specification document to generate test cases.

Analyze the document content below and identify information gaps — things that are ambiguous, missing, or unclear that would prevent thorough test case generation.

Generate up to 10 clarifying questions. Each question must be:
- Specific and answerable in 1-2 sentences
- Focused on testable behavior (not opinions)
- Ordered by importance (most critical first)

Respond ONLY as a JSON object:
{{
  "gaps_found": [string],
  "questions": [
    {{
      "id": 1,
      "question": string,
      "why_needed": string,
      "category": "Functional" | "Edge Case" | "Integration" | "Security" | "Performance" | "Data Validation"
    }}
  ],
  "doc_summary": string
}}

Limit to maximum 10 questions. Only ask what genuinely impacts test coverage.

Document content:
{content}
"""

EXTRACT_ENTITIES_PROMPT = """You are a technical analyst building a knowledge graph for test case generation.

Given the document content AND additional context from user answers to clarifying questions, extract structured entities.

Additional context from user Q&A:
{qa_context}

Respond ONLY as a JSON object:
{{
  "features": [{{"name": string, "description": string}}],
  "user_roles": [{{"role": string, "permissions": [string]}}],
  "actions": [{{"action": string, "actor": string, "target": string, "preconditions": [string]}}],
  "business_rules": [{{"rule": string, "applies_to": string, "condition": string}}],
  "data_entities": [{{"entity": string, "fields": [string], "constraints": [string]}}],
  "edge_cases": [{{"scenario": string, "expected_behavior": string}}]
}}

Document content:
{content}
"""

MERGE_GRAPHS_PROMPT = """Merge the following knowledge graphs into one coherent graph. Remove duplicates, resolve conflicts.

Respond ONLY as JSON with the same schema:
{{
  "features": [...],
  "user_roles": [...],
  "actions": [...],
  "business_rules": [...],
  "data_entities": [...],
  "edge_cases": [...]
}}

Graphs:
{graphs}
"""

GENERATE_TESTCASES_PROMPT = """You are a senior QA engineer. Using the knowledge graph and user-provided context below, generate comprehensive test cases.

Cover:
- Happy path scenarios for each feature
- Negative / error scenarios
- Edge cases from the graph
- Role-based access control scenarios
- Data validation scenarios
- Integration/flow scenarios
- Performance boundary scenarios where applicable

For each test case provide:
- Unique Test ID (TC_001, TC_002 ...)
- Module / Feature
- Title
- Description
- Preconditions
- Test Steps (numbered, as a single string)
- Expected Result
- Priority (High / Medium / Low)
- Test Type (Functional / Negative / Edge Case / Integration / Performance / Security)
- User Role

Respond ONLY as a JSON array:
[
  {{
    "test_id": string,
    "module": string,
    "title": string,
    "description": string,
    "preconditions": string,
    "test_steps": string,
    "expected_result": string,
    "priority": "High" | "Medium" | "Low",
    "test_type": string,
    "user_role": string
  }}
]

Generate minimum 15 test cases. Cover ALL features, roles, and edge cases present in the graph.

User Q&A context:
{qa_context}

Knowledge Graph:
{knowledge_graph}
"""

CONFLUENCE_SUMMARIZE_PROMPT = """Summarize the following Confluence page content, extracting only information relevant to software requirements, features, user flows, and business rules. Remove navigation, metadata, and boilerplate.

Return clean plain text only.

Content:
{content}
"""

SUMMARIZE_DOCUMENT_PROMPT = """Provide a concise 2-3 sentence summary of this document focusing on its purpose and the system/feature it covers.

Document:
{content}
"""
