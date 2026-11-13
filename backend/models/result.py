from pydantic import BaseModel
from typing import Optional


class Finding(BaseModel):
    name: str
    status: str
    severity: str
    description: str
    recommendation: Optional[str] = None


class ScanResult(BaseModel):
    url: str
    score: int
    findings: list[Finding]