"""
main.py - FastAPI backend for the Test Case Generator.
"""

import os
import uuid
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from ingestion import ingest_multiple_files
from graph import build_knowledge_graph
from generation import generate_test_cases, get_generation_summary
from export import export_test_cases

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Test Case Generator API",
    description="AI-powered test case generation from spec documents",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for generated Excel files
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".docx"}


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "testcase-generator"}


# ── Chat endpoint ─────────────────────────────────────────────────────────────

@app.post("/chat")
async def chat(
    message: str = Form(...),
    openai_api_key: str = Form(...),
    files: list[UploadFile] = File(default=[]),
):
    """
    Main endpoint. Accepts a user message + optional files.
    If files are provided, runs the full pipeline.
    Otherwise returns a conversational response.
    """
    # Validate files
    uploaded_files = []
    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File '{f.filename}' has unsupported type '{ext}'. "
                       f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )
        content = await f.read()
        uploaded_files.append({"filename": f.filename, "bytes": content})

    if not uploaded_files:
        # No files — just echo a helpful message
        return JSONResponse({
            "type": "message",
            "content": (
                "👋 Hello! I'm your Test Case Generator. "
                "Please upload your spec documents (PDF, XLSX, or DOCX) "
                "and I'll generate comprehensive test cases for you. "
                "Use the **+** button to attach files, then send your message."
            ),
            "download_url": None,
            "stats": None,
        })

    # ── Run the pipeline ─────────────────────────────────────────────────
    try:
        # Step 1 — Ingest
        logger.info(f"Ingesting {len(uploaded_files)} file(s)...")
        ingested = ingest_multiple_files(uploaded_files)

        failed = [d for d in ingested if d["status"] == "error"]
        if len(failed) == len(ingested):
            errors = "; ".join(f"{d['filename']}: {d['error']}" for d in failed)
            raise HTTPException(status_code=422, detail=f"All files failed ingestion: {errors}")

        if failed:
            logger.warning(f"{len(failed)} file(s) failed: {[d['filename'] for d in failed]}")

        # Step 2 — Build knowledge graph
        logger.info("Building knowledge graph...")
        graph_result = build_knowledge_graph(openai_api_key, ingested)

        # Step 3 — Generate test cases
        logger.info("Generating test cases...")
        test_cases = generate_test_cases(openai_api_key, graph_result["graph"])
        summary = get_generation_summary(test_cases)

        # Step 4 — Export to Excel
        logger.info("Exporting to Excel...")
        job_id = str(uuid.uuid4())[:8]
        filename = f"testcases_{job_id}.xlsx"
        output_path = OUTPUT_DIR / filename

        export_test_cases(
            test_cases=test_cases,
            summary=summary,
            doc_summaries=graph_result["summaries"],
            output_path=str(output_path),
        )

        download_url = f"/download/{filename}"

        # Build a rich response message
        stats = graph_result["stats"]
        response_text = (
            f"✅ **Done!** I've analysed **{stats['documents_processed']} document(s)** and generated "
            f"**{summary['total']} test cases** covering:\n\n"
            f"- 🔧 {stats['features_found']} features / modules\n"
            f"- 👤 {stats['user_roles_found']} user roles\n"
            f"- ⚡ {stats['actions_found']} user actions\n"
            f"- 📋 {stats['business_rules_found']} business rules\n"
            f"- 🚨 {stats['edge_cases_found']} edge cases\n\n"
            f"**Priority breakdown:** "
            f"🔴 High: {summary['by_priority'].get('High', 0)}  "
            f"🟡 Medium: {summary['by_priority'].get('Medium', 0)}  "
            f"🟢 Low: {summary['by_priority'].get('Low', 0)}\n\n"
            f"Your Excel report is ready to download! 👇"
        )

        return JSONResponse({
            "type": "result",
            "content": response_text,
            "download_url": download_url,
            "filename": filename,
            "stats": {**stats, **summary},
            "failed_files": [d["filename"] for d in failed],
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Pipeline failed")
        raise HTTPException(status_code=500, detail=str(e))


# ── File download ─────────────────────────────────────────────────────────────

@app.get("/download/{filename}")
def download_file(filename: str):
    """Serve the generated Excel file for download."""
    # Security: only allow safe filenames
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found. It may have expired.")
    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Cleanup old files (optional background task) ──────────────────────────────

def _cleanup_old_outputs(max_files: int = 50):
    """Keep only the N most recent output files."""
    files = sorted(OUTPUT_DIR.glob("*.xlsx"), key=lambda f: f.stat().st_mtime, reverse=True)
    for old_file in files[max_files:]:
        old_file.unlink(missing_ok=True)
        logger.info(f"Cleaned up old file: {old_file.name}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
