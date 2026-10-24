# JD & Resume Intelligence Platform (Prototype)

A free, deterministic-first Python starter project for:
- Uploading resume/JD PDFs
- Extracting selectable PDF text
- Finding skills using a curated alias dictionary
- Keeping evidence snippets and source page numbers
- Exporting standardized JSON
- Matching a resume against user-specified required/preferred JD skills
- Serving a FastAPI API and a Streamlit UI

## Quick start (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app/ui.py
```

Open the local Streamlit URL shown in the terminal.

## Run the API instead

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to try the API.

### API endpoints
- `GET /health` — health check
- `POST /parse` — form fields: `file` (PDF), `document_type` (`resume` or `job_description`)
- `POST /match` — form fields: `resume_file`, `jd_file`, `required_skills` (comma-separated), `preferred_skills` (comma-separated)

## Project structure

```text
jd_resume_intelligence_platform/
├── app/
│   ├── parser.py       # PDF extraction, skill dictionary, evidence
│   ├── matching.py     # Explainable skill-overlap baseline
│   ├── schemas.py      # Pydantic schema definitions
│   ├── main.py         # FastAPI backend
│   └── ui.py           # Streamlit frontend
├── data/
│   ├── uploads/        # Local temporary uploads
│   └── outputs/        # API JSON outputs
├── tests/
├── requirements.txt
└── README.md
```

## Important limitations

This is a runnable baseline, not a validated production parser:
1. The skill dictionary is limited; extend it based on your target job families.
2. Required vs preferred JD skills are supplied manually in the match UI/API. Automatic classification is not implemented because simple heading/rule heuristics can mislabel requirements.
3. Scanned PDFs need OCR. This package detects empty text but does not run OCR automatically.
4. Section extraction is heuristic and may not capture every resume layout.
5. Match score is an illustrative skill overlap, not a hiring recommendation.
6. Precision >85% has not been established. Build a gold dataset with manually labelled skill mentions, test on all 70 documents, and calculate precision/recall before claiming that target.
7. Add authentication, privacy controls, file cleanup, malware scanning, and deployment hardening before handling real candidate data.

## Evaluation formula

`precision = TP / (TP + FP) * 100`

Where TP is a correct extracted skill and FP is a skill unsupported by the source document. Also measure recall to find missed skills.

## Suggested next steps

1. Label the 20 JD and 50 resume samples manually.
2. Expand the dictionary and aliases based on actual false positives/negatives.
3. Add OCR fallback with Tesseract for scanned PDFs.
4. Implement tested JD requirement classification and experience/education extraction.
5. Add batch upload and an evaluation report with per-document metrics.
