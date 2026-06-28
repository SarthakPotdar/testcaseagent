# 🧪 TestCase Agent v2.1

AI-powered test case generator — gap analysis Q&A, Confluence, in-memory pipeline, multilingual UI, dual export (XLSX + CSV).

## Project Structure

```
testcaseagent/
├── backend/
│   ├── main.py           # FastAPI — all routes
│   ├── session_store.py  # Pure in-memory session storage (no disk)
│   ├── ingestion.py      # PDF / XLSX / DOCX text extraction
│   ├── confluence.py     # Confluence fetch + credential verification
│   ├── gap_analysis.py   # Spec gap detection → up to 10 questions
│   ├── graph.py          # Knowledge graph builder (GPT-4o-mini)
│   ├── generation.py     # Test case generator (GPT-4o-mini)
│   ├── export.py         # XLSX + CSV as bytes (no files written)
│   ├── prompts.py        # All LLM prompts
│   └── requirements.txt
├── frontend/
│   ├── app.py            # Streamlit chat UI
│   ├── i18n.py           # Translations: EN / ES / JA / KO
│   └── requirements.txt
└── README.md
```

## Quick Start

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (new terminal)
cd frontend && pip install -r requirements.txt
streamlit run app.py
```

## Key Design Decisions

### ✅ Fully In-Memory Pipeline
- Uploaded file bytes held in RAM during the request
- Session data (doc content + questions) stored in a Python dict with TTL (2 hrs)
- Export bytes returned as base64 in JSON — no temp files written anywhere
- Background thread cleans expired sessions every 30 mins

### ✅ Min 2 Answers Before Submit
- Submit button stays disabled until user fills at least 2 question fields
- Counter shown live as answers are typed
- Skip button always available to bypass Q&A entirely

### ✅ Language Support
Dropdown in sidebar switches the entire UI:
| Language | Code |
|---|---|
| English | en |
| Español | es |
| 日本語 | ja |
| 한국어 | ko |

All labels, buttons, placeholders, hints, and messages translate instantly.

### ✅ Dual Export
- **Excel (.xlsx)** — styled, colour-coded priority, summary sheet, filters
- **CSV (.csv)** — UTF-8 with BOM (Excel compatible)
- Both served as inline base64 data URIs — no `/download/` route needed

## Pipeline Flow

```
1. /analyze  — Ingest files/Confluence → gap analysis → save session in memory → return questions
2. User fills Q&A in chat (min 2 answers, 1000 char limit each)
3. /generate — Load session → build graph → generate TCs → export → delete session → return base64 files
```

## Confluence Setup

1. `https://id.atlassian.com/manage-profile/security/api-tokens` → create token
2. Use your Atlassian email as User ID
3. URL: `https://yourorg.atlassian.net/wiki`
4. Click **Verify Access** before uploading

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Status + active session count |
| POST | `/verify-confluence` | Check Confluence credentials |
| POST | `/analyze` | Ingest + gap analysis → return questions |
| POST | `/generate` | Q&A + graph + generation → base64 files |
