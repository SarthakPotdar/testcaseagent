# 🧪 TestGen AI — AI-Powered Test Case Generator

Generate comprehensive test cases from spec documents (PDF, XLSX, DOCX) using OpenAI GPT-4o-mini and a knowledge graph pipeline.

## Architecture

```
testcase_gen/
├── backend/
│   ├── main.py          # FastAPI app — routes & orchestration
│   ├── ingestion.py     # File parsing (PDF / XLSX / DOCX → text)
│   ├── graph.py         # Knowledge graph builder (OpenAI)
│   ├── generation.py    # Test case generator (OpenAI)
│   ├── export.py        # Excel report exporter (openpyxl)
│   ├── prompts.py       # All LLM prompts
│   └── requirements.txt
├── frontend/
│   ├── app.py           # Streamlit chat UI
│   └── requirements.txt
└── README.md
```

## Pipeline

```
Upload files (PDF/XLSX/DOCX)
        │
        ▼
  ingestion.py          — Extract raw text from files
        │
        ▼
  graph.py              — Build knowledge graph via GPT-4o-mini
        │                 (features, roles, actions, rules, edge cases)
        ▼
  generation.py         — Generate test cases from knowledge graph
        │
        ▼
  export.py             — Format into professional Excel report
        │
        ▼
  Download URL returned to frontend
```

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be live at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

The UI opens at `http://localhost:8501`.

### 3. Usage

1. Open `http://localhost:8501`
2. Enter your OpenAI API key in the sidebar
3. Click the sidebar file uploader to attach spec docs
4. Type a message (e.g. "Generate test cases for these specs") and hit Enter
5. Download the Excel report when it's ready

## Supported File Types

| Format | What's extracted |
|--------|-----------------|
| `.pdf` | Text content + tables from all pages |
| `.xlsx` / `.xls` | All cell values from every sheet |
| `.docx` | Paragraphs + table contents |

## Excel Output

The generated report has two sheets:

- **Test Cases** — Full test case table with columns: Test ID, Module, Title, Description, Preconditions, Test Steps, Expected Result, Priority, Test Type, User Role. Priority cells are colour-coded (🔴 High / 🟡 Medium / 🟢 Low).
- **Summary** — Dashboard with counts by priority, test type, module, and document summaries.

## Environment Variables (optional)

You can set a default API key instead of entering it in the UI:

```bash
export OPENAI_API_KEY=sk-...
```

## Notes

- Uses `gpt-4o-mini` for all LLM calls (cost-efficient).
- Large documents are automatically chunked and merged.
- Multiple files are processed individually then merged into one graph.
- Generated Excel files are stored in `backend/outputs/` (auto-cleaned after 50 files).
