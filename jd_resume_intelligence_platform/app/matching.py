"""Explainable baseline resume-to-JD matching."""
from app.parser import SKILL_ALIASES
import re

def canonicalize_skill(value: str) -> str:
    normalized = value.strip().lower()
    for canonical, aliases in SKILL_ALIASES.items():
        if normalized == canonical.lower() or normalized in [a.lower() for a in aliases]:
            return canonical
    return value.strip()

def match_resume_to_jd(resume: dict, jd: dict) -> dict:
    resume_skill_map = {canonicalize_skill(item["name"]): item for item in resume.get("skills", [])}
    required = {canonicalize_skill(s) for s in jd.get("required_skills", [])}
    preferred = {canonicalize_skill(s) for s in jd.get("preferred_skills", [])}
    required_matched = sorted(required & set(resume_skill_map))
    preferred_matched = sorted(preferred & set(resume_skill_map))
    missing_required = sorted(required - set(resume_skill_map))
    required_score = (len(required_matched) / len(required) * 80) if required else 80.0
    preferred_score = (len(preferred_matched) / len(preferred) * 20) if preferred else 20.0
    evidence = []
    for skill in required_matched + preferred_matched:
        item = resume_skill_map[skill]
        evidence.append({
            "skill": skill,
            "evidence": item.get("evidence", ""),
            "source_page": item.get("source_page"),
        })
    return {
        "score": round(required_score + preferred_score, 2),
        "score_note": "Illustrative skill-overlap score only; not a hiring decision or validated predictor.",
        "matched_required_skills": required_matched,
        "missing_required_skills": missing_required,
        "matched_preferred_skills": preferred_matched,
        "evidence": evidence,
    }
