"""Streamlit UI for uploading PDFs and viewing/download JSON."""
import json
from pathlib import Path
import streamlit as st
from app.parser import parse_document
from app.matching import match_resume_to_jd
from app.parser import parse_document

st.set_page_config(page_title="JD & Resume Intelligence", page_icon="📄", layout="wide")
st.title("📄 JD & Resume Intelligence")
st.caption("Deterministic-first PDF parsing prototype • evidence-backed skill extraction")

with st.sidebar:
    st.header("About this prototype")
    st.write("Uses local Python rules and a curated skill dictionary. No LLM API required.")
    st.warning("Scanned PDFs need OCR. Review all extracted data before use in hiring workflows.")

tab_parse, tab_match = st.tabs(["PDF → JSON", "Resume ↔ JD Match"])

with tab_parse:
    uploaded = st.file_uploader("Upload a resume or JD PDF", type=["pdf"], key="parse_pdf")
    kind = st.radio("Document type", ["resume", "job_description"], horizontal=True)
    if uploaded and st.button("Parse PDF", type="primary"):
        temp = Path("data/uploads") / uploaded.name
        temp.parent.mkdir(parents=True, exist_ok=True)
        temp.write_bytes(uploaded.getvalue())
        try:
            result = parse_document(str(temp), kind)
            st.subheader("Extracted skills")
            st.write([s["name"] for s in result["skills"]])
            if result["warnings"]:
                st.warning(" ".join(result["warnings"]))
            st.subheader("JSON output")
            st.json(result)
            st.download_button("Download JSON", json.dumps(result, indent=2, ensure_ascii=False),
                               file_name=f"{temp.stem}_{kind}.json", mime="application/json")
        except Exception as exc:
            st.error(f"Parsing failed: {exc}")

with tab_match:
    left, right = st.columns(2)
    with left:
        resume_file = st.file_uploader("Upload resume PDF", type=["pdf"], key="resume_match")
    with right:
        jd_file = st.file_uploader("Upload JD PDF", type=["pdf"], key="jd_match")
    req = st.text_input("Required skills (comma-separated)", placeholder="Python, Django, REST API")
    pref = st.text_input("Preferred skills (comma-separated)", placeholder="Docker, AWS")
    if st.button("Match resume to JD", type="primary"):
        if not resume_file or not jd_file:
            st.error("Upload both PDFs first.")
        else:
            try:
                Path("data/uploads").mkdir(parents=True, exist_ok=True)
                rpath = Path("data/uploads") / resume_file.name
                jpath = Path("data/uploads") / jd_file.name
                rpath.write_bytes(resume_file.getvalue())
                jpath.write_bytes(jd_file.getvalue())
                resume = parse_document(str(rpath), "resume")
                jd_parsed = parse_document(str(jpath), "job_description")
                jd = {
                    "required_skills": [x.strip() for x in req.split(",") if x.strip()],
                    "preferred_skills": [x.strip() for x in pref.split(",") if x.strip()],
                    "extracted_skills": jd_parsed["skills"],
                    "raw_text": jd_parsed["raw_text"]
                }
                result = {"resume": resume, "job_description": jd,
                          "match": match_resume_to_jd(resume, jd)}
                st.metric("Illustrative match score", f'{result["match"]["score"]}%')
                st.write("Matched required:", result["match"]["matched_required_skills"])
                st.write("Missing required:", result["match"]["missing_required_skills"])
                st.write("Matched preferred:", result["match"]["matched_preferred_skills"])
                st.json(result)
                st.download_button("Download match JSON",
                    json.dumps(result, indent=2, ensure_ascii=False),
                    file_name="resume_jd_match.json", mime="application/json")
            except Exception as exc:
                st.error(f"Matching failed: {exc}")
