"""Deterministic PDF text extraction and evidence-backed skill extraction."""
from pathlib import Path
import re
import pymupdf

SKILL_ALIASES = {
    "Python": ["python"],
    "Java": ["java"],
    "C++": ["c++"],
    "C": ["c language", "programming in c"],
    "JavaScript": ["javascript", "java script"],
    "TypeScript": ["typescript"],
    "SQL": ["sql", "structured query language"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "Django": ["django"],
    "FastAPI": ["fastapi"],
    "Flask": ["flask"],
    "REST API": ["rest api", "restful api", "rest apis"],
    "Machine Learning": ["machine learning"],
    "Deep Learning": ["deep learning"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "React": ["react.js", "reactjs", "react"],
    "Next.js": ["next.js", "nextjs"],
    "Node.js": ["node.js", "nodejs"],
    "HTML": ["html"],
    "CSS": ["css"],
    "Tailwind CSS": ["tailwind css", "tailwind"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes"],
    "AWS": ["amazon web services", "aws"],
    "Azure": ["microsoft azure", "azure"],
    "GCP": ["google cloud platform", "gcp"],
    "Linux": ["linux"],
    "Agile": ["agile"],
    "Scrum": ["scrum"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Excel": ["microsoft excel", "excel"],
    "Power BI": ["power bi"],
    "Tableau": ["tableau"],
    "Communication": ["communication skills"],
}

def extract_pdf_pages(pdf_path: str) -> list[dict]:
    """Extract text page-by-page. Scanned PDFs may require OCR."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    pages = []
    with pymupdf.open(path) as doc:
        for idx, page in enumerate(doc, start=1):
            pages.append({"page": idx, "text": page.get_text("text") or ""})
    return pages

def _alias_pattern(alias: str) -> re.Pattern:
    # Use word boundaries to reduce accidental substring matches.
    return re.compile(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", re.IGNORECASE)

def extract_skills(pages: list[dict]) -> list[dict]:
    """Extract known skills with literal source evidence and page numbers."""
    found = {}
    for page in pages:
        text = page["text"]
        for canonical, aliases in SKILL_ALIASES.items():
            if canonical in found:
                continue
            for alias in aliases:
                match = _alias_pattern(alias).search(text)
                if match:
                    start = max(0, match.start() - 70)
                    end = min(len(text), match.end() + 70)
                    found[canonical] = {
                        "name": canonical,
                        "matched_alias": alias,
                        "evidence": text[start:end].strip(),
                        "source_page": page["page"],
                        "extraction_method": "dictionary_rule",
                    }
                    break
    return sorted(found.values(), key=lambda item: item["name"].lower())

def extract_sections(text: str) -> dict:
    """Lightweight heuristic section extraction; review output for real documents."""
    headings = {
        "skills": r"skills|technical skills|core competencies",
        "experience": r"experience|employment|work history|internship",
        "education": r"education|academic background|qualifications",
        "projects": r"projects|personal projects|academic projects",
        "certifications": r"certifications|certificates|licenses",
    }
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections = {name: [] for name in headings}
    current = None
    for line in lines:
        normalized = line.strip(" :|-\t").lower()
        matched = None
        for name, pattern in headings.items():
            if re.fullmatch(pattern, normalized, flags=re.IGNORECASE):
                matched = name
                break
        if matched:
            current = matched
        elif current:
            sections[current].append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items()}

def parse_document(pdf_path: str, document_type: str) -> dict:
    if document_type not in {"resume", "job_description"}:
        raise ValueError("document_type must be 'resume' or 'job_description'")
    pages = extract_pdf_pages(pdf_path)
    full_text = "\n".join(page["text"] for page in pages)
    return {
        "schema_version": "1.0",
        "document_type": document_type,
        "filename": Path(pdf_path).name,
        "page_count": len(pages),
        "skills": extract_skills(pages),
        "sections": extract_sections(full_text),
        "raw_text": full_text,
        "warnings": (
            ["No selectable text found; this may be a scanned PDF requiring OCR."]
            if not full_text.strip() else []
        ),
    }
