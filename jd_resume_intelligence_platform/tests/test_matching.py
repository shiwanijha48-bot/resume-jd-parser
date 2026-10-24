from app.matching import match_resume_to_jd

def test_match_required_and_preferred():
    resume = {
        "skills": [
            {"name": "Python", "evidence": "Python project", "source_page": 1},
            {"name": "Django", "evidence": "Django app", "source_page": 2},
        ]
    }
    jd = {
        "required_skills": ["Python", "Django", "REST API"],
        "preferred_skills": ["AWS"]
    }
    result = match_resume_to_jd(resume, jd)
    assert result["matched_required_skills"] == ["Django", "Python"]
    assert result["missing_required_skills"] == ["REST API"]
    assert result["score"] == 53.33

def test_empty_requirements():
    result = match_resume_to_jd({"skills": []}, {
        "required_skills": [], "preferred_skills": []
    })
    assert result["score"] == 100.0
