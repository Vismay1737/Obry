from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Optional
from datetime import datetime, timezone

class Vulnerability(BaseModel):
    title: str
    severity: str # high, medium, low
    description: str
    recommendation: str

class ScanRequest(BaseModel):
    target: str

class ScanResult(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    target: str
    status: str  # running, completed, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    raw_output: Dict[str, str] = {}  # {"nmap": "...", "nikto": "...", etc.}
    ai_analysis: Optional[str] = None
    security_score: Optional[int] = None
    vulnerabilities: list[Vulnerability] = []

    model_config = ConfigDict(populate_by_name=True)
