"""
All LLM prompts used throughout the pipeline.
"""

EXTRACT_ENTITIES_PROMPT = """You are a technical analyst. Given the following document content, extract structured information to build a knowledge graph for test case generation.

Extract:
1. **Features / Modules** - Named features, modules, screens, components
2. **User Roles** - Types of users (admin, guest, customer, etc.)
3. **Actions / Flows** - Key user actions, workflows, API calls
4. **Business Rules** - Conditions, validations, constraints
5. **Data Entities** - Key data objects, fields, and types
6. **Edge Cases** - Explicitly mentioned edge/error cases

Respond ONLY as a JSON object with this exact schema:
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

MERGE_GRAPHS_PROMPT = """You are a knowledge graph expert. Merge the following multiple entity graphs extracted from different documents into a single coherent knowledge graph. 

Remove duplicates (merge entities with the same or similar names), resolve conflicts, and enrich entities with combined information.

Respond ONLY as a JSON object with the same schema:
{{
  "features": [...],
  "user_roles": [...],
  "actions": [...],
  "business_rules": [...],
  "data_entities": [...],
  "edge_cases": [...]
}}

Graphs to merge:
{graphs}
"""

GENERATE_TESTCASES_PROMPT = """You are a senior QA engineer. Using the knowledge graph below, generate comprehensive test cases covering:
- Happy path scenarios for each feature
- Negative / error scenarios
- Edge cases from the graph
- Role-based access scenarios
- Data validation scenarios
- Integration/flow scenarios

For each test case provide:
- A unique Test ID (TC_001, TC_002, ...)
- Module / Feature name
- Test Case Title
- Description
- Preconditions
- Test Steps (numbered list as a single string)
- Expected Result
- Priority (High / Medium / Low)
- Test Type (Functional / Negative / Edge Case / Integration / Performance / Security)
- User Role involved

Respond ONLY as a JSON array of test case objects:
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
  }},
  ...
]

Generate at minimum 15 test cases. Cover all features, roles, and edge cases present in the graph.

Knowledge Graph:
{knowledge_graph}
"""

SUMMARIZE_DOCUMENT_PROMPT = """Provide a concise 2-3 sentence summary of what this document describes, focusing on its purpose and the system/feature it covers.

Document:
{content}
"""
