"""
main.py - FastAPI backend for the Test Case Agent.
All session data and file content stored in memory — nothing written to disk.
"""

import uuid
import logging
import base64
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingestion import ingest_multiple_files
from gap_analysis import analyze_gaps, format_qa_context
from graph import build_knowledge_graph
from generation import generate_test_cases, get_summary
from export import create_xlsx_bytes, create_csv_bytes
from confluence import (verify_confluence_access, fetch_confluence_page,
                        fetch_confluence_space, summarize_confluence_content)
from session_store import save_session, get_session, delete_session, active_session_count

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Test Case Agent API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

ALLOWED_EXT = {".pdf", ".xlsx", ".xls", ".docx"}


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "active_sessions": active_session_count()}


# ── Verify Confluence ─────────────────────────────────────────────────────────

class ConfluenceVerifyReq(BaseModel):
    confluence_url: str
    confluence_api_key: str
    confluence_user_id: str


@app.post("/verify-confluence")
async def verify_confluence(req: ConfluenceVerifyReq):
    result = verify_confluence_access(req.confluence_url, req.confluence_api_key, req.confluence_user_id)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    return {"success": True, "message": f"Verified: {result['user_display_name']}", "user_display_name": result["user_display_name"]}


# ── Step 1: Analyze ───────────────────────────────────────────────────────────

@app.post("/analyze")
async def analyze(
    openai_api_key: str = Form(...),
    files: list[UploadFile] = File(default=[]),
    confluence_url: str = Form(default=""),
    confluence_api_key: str = Form(default=""),
    confluence_user_id: str = Form(default=""),
    confluence_page_id: str = Form(default=""),
    confluence_space_key: str = Form(default=""),
):
    """
    Ingest files + Confluence into memory.
    Run gap analysis.
    Store everything in memory session.
    Return questions.
    """
    # Validate + read files into memory immediately
    uploaded = []
    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOWED_EXT:
            raise HTTPException(status_code=400,
                detail=f"'{f.filename}' has unsupported type '{ext}'. Allowed: {', '.join(ALLOWED_EXT)}")
        content_bytes = await f.read()   # read into memory
        uploaded.append({"filename": f.filename, "bytes": content_bytes})

    # Ingest files — extract text in memory
    ingested_docs = ingest_multiple_files(uploaded) if uploaded else []
    successful = [d for d in ingested_docs if d["status"] == "success"]
    failed = [d for d in ingested_docs if d["status"] == "error"]

    # Confluence
    confluence_docs = []
    confluence_errors = []
    if confluence_url and confluence_api_key and confluence_user_id:
        if confluence_page_id:
            page = fetch_confluence_page(confluence_url, confluence_api_key, confluence_user_id, confluence_page_id)
            if page["success"]:
                summ = summarize_confluence_content(openai_api_key, page["content"])
                confluence_docs.append({"filename": f"Confluence: {page['title']}", "content": summ, "status": "success", "char_count": len(summ)})
            else:
                confluence_errors.append(page["error"])
        elif confluence_space_key:
            for page in fetch_confluence_space(confluence_url, confluence_api_key, confluence_user_id, confluence_space_key):
                if page["success"] and page["content"]:
                    summ = summarize_confluence_content(openai_api_key, page["content"])
                    confluence_docs.append({"filename": f"Confluence: {page['title']}", "content": summ, "status": "success", "char_count": len(summ)})

    all_docs = successful + confluence_docs
    if not all_docs:
        err = "; ".join(d["error"] for d in failed) if failed else "No files or Confluence content provided."
        raise HTTPException(status_code=422, detail=f"No content to analyze. {err}")

    # Combined content for gap analysis
    combined = "\n\n===\n\n".join(f"[{d['filename']}]\n{d['content']}" for d in all_docs)

    # Gap analysis
    logger.info("Running gap analysis...")
    gap_result = analyze_gaps(openai_api_key, combined)

    # Store everything in memory — no disk
    session_id = str(uuid.uuid4())[:12]
    save_session(session_id, {
        "openai_api_key": openai_api_key,
        "all_docs": [{"filename": d["filename"], "content": d["content"], "status": "success"} for d in all_docs],
        "gap_result": gap_result,
    })

    logger.info(f"Session {session_id} created. Docs: {len(all_docs)}, Questions: {gap_result['question_count']}")

    return JSONResponse({
        "session_id": session_id,
        "doc_summary": gap_result["doc_summary"],
        "question_count": gap_result["question_count"],
        "questions": gap_result["questions"],
        "gaps_found": gap_result["gaps_found"],
        "files_processed": [d["filename"] for d in all_docs],
        "failed_files": [{"filename": d["filename"], "error": d["error"]} for d in failed],
        "confluence_errors": confluence_errors,
    })


# ── Step 2: Generate ──────────────────────────────────────────────────────────

@app.post("/generate")
async def generate(
    session_id: str = Form(...),
    answers: str = Form(...),
):
    """
    Load session from memory.
    Build graph + generate test cases + export.
    Return file bytes as base64 in JSON (avoids filesystem entirely).
    """
    import json as _json

    # Load session from memory
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404,
            detail="Session not found or expired. Sessions last 2 hours — please re-upload your files.")

    try:
        answers_dict = _json.loads(answers)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid answers format.")

    # Enforce 1000 char limit per answer
    for qid, ans in answers_dict.items():
        if len(str(ans)) > 1000:
            raise HTTPException(status_code=400, detail=f"Answer to Q{qid} exceeds 1000 characters.")

    openai_api_key = session["openai_api_key"]
    all_docs = session["all_docs"]
    questions = session["gap_result"]["questions"]

    qa_context = format_qa_context(questions, answers_dict)

    try:
        # Build knowledge graph in memory
        logger.info(f"Building graph for session {session_id}...")
        graph_result = build_knowledge_graph(openai_api_key, all_docs, qa_context)

        # Generate test cases
        logger.info("Generating test cases...")
        test_cases = generate_test_cases(openai_api_key, graph_result["graph"], qa_context)
        summary = get_summary(test_cases)

        # Export to bytes — no files written
        logger.info("Exporting to XLSX + CSV bytes...")
        xlsx_bytes = create_xlsx_bytes(test_cases, summary, graph_result["summaries"])
        csv_bytes = create_csv_bytes(test_cases)

        # Delete session from memory — no longer needed
        delete_session(session_id)

        stats = graph_result["stats"]
        response_text = (
            f"Done! Analysed **{stats['documents_processed']} document(s)** and generated "
            f"**{summary['total']} test cases** covering:\n\n"
            f"- {stats['features_found']} features\n"
            f"- {stats['user_roles_found']} user roles\n"
            f"- {stats['actions_found']} actions\n"
            f"- {stats['business_rules_found']} business rules\n"
            f"- {stats['edge_cases_found']} edge cases\n\n"
            f"Priority — High: {summary['by_priority'].get('High',0)}  "
            f"Medium: {summary['by_priority'].get('Medium',0)}  "
            f"Low: {summary['by_priority'].get('Low',0)}\n\n"
            f"Your reports are ready to download!"
        )

        return JSONResponse({
            "success": True,
            "content": response_text,
            "stats": {**stats, **summary},
            # Return file bytes as base64 so frontend can offer direct download
            "xlsx_b64": base64.b64encode(xlsx_bytes).decode(),
            "csv_b64": base64.b64encode(csv_bytes).decode(),
            "xlsx_filename": f"testcases_{session_id}.xlsx",
            "csv_filename": f"testcases_{session_id}.csv",
        })

    except Exception as e:
        logger.exception("Generation failed")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
