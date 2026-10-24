"""Pydantic request/response schemas."""
from pydantic import BaseModel, Field
from typing import Literal

class SkillEvidence(BaseModel):
    name: str
    matched_alias: str | None = None
    evidence: str
    source_page: int = Field(ge=1)
    extraction_method: str = "dictionary_rule"

class ParsedDocument(BaseModel):
    schema_version: str = "1.0"
    document_type: Literal["resume", "job_description"]
    filename: str
    page_count: int
    skills: list[SkillEvidence]
    sections: dict[str, str]
    raw_text: str
    warnings: list[str] = []
