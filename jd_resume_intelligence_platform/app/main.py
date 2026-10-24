"""FastAPI service for PDF parsing, JD JSON, and resume matching."""
from pathlib import Path
import json
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.parser import parse_document
from app.matching import match_resume_to_jd

ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIR = ROOT / "data" / "uploads"
OUTPUT_DIR = ROOT / "data" / "outputs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="JD & Resume Intelligence API", version="1.0.0",
              description="Rule-based PDF extraction with evidence-backed skills. Baseline prototype.")

def save_json(data: dict, name: str) -> Path:
    path = OUTPUT_DIR / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

async def store_pdf(file: UploadFile) -> Path:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Upload a .pdf file.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds the 20 MB prototype limit.")
    name = f"{uuid.uuid4().hex}_{Path(file.filename).name}"
    path = UPLOAD_DIR / name
    path.write_bytes(content)
    return path

@app.get("/")
def root():
    return {"message": "JD & Resume Intelligence API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/parse")
async def parse_pdf(file: UploadFile = File(...),
                    document_type: str = Form(...)):
    if document_type not in {"resume", "job_description"}:
        raise HTTPException(status_code=400, detail="document_type must be resume or job_description")
    path = await store_pdf(file)
    try:
        result = parse_document(str(path), document_type)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse PDF: {exc}")
    out_name = f"{Path(file.filename).stem}_{document_type}.json"
    save_json(result, out_name)
    return JSONResponse(result)

@app.post("/match")
async def match_pdf(resume_file: UploadFile = File(...),
                    jd_file: UploadFile = File(...),
                    required_skills: str = Form(""),
                    preferred_skills: str = Form("")):
    resume_path = await store_pdf(resume_file)
    jd_path = await store_pdf(jd_file)
    try:
        resume = parse_document(str(resume_path), "resume")
        jd_parsed = parse_document(str(jd_path), "job_description")
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse PDF: {exc}")
    # Explicit skill lists are supplied by the user for this baseline.
    # Automatic required/preferred classification is not reliable enough to assume.
    jd = {
        "document_type": "job_description",
        "filename": Path(jd_file.filename).name,
        "required_skills": [s.strip() for s in required_skills.split(",") if s.strip()],
        "preferred_skills": [s.strip() for s in preferred_skills.split(",") if s.strip()],
        "extracted_skills": jd_parsed["skills"],
        "raw_text": jd_parsed["raw_text"],
        "warning": "Required/preferred skills are manually supplied in this baseline; automatic classification is not implemented."
    }
    result = {
        "resume": resume,
        "job_description": jd,
        "match": match_resume_to_jd(resume, jd)
    }
    save_json(result, f"match_{uuid.uuid4().hex[:10]}.json")
    return JSONResponse(result)
