from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ScanRequest(BaseModel):
    target: str

class VulnerabilityIssue(BaseModel):
    title: str
    severity: str # Low, Medium, High, Critical
    description: str
    recommendation: str

class ScanResult(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    target: str
    status: str # pending, running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    raw_output: Dict[str, str] = {} # e.g. {"nmap": "...", "nikto": "..."}
    ai_analysis: Optional[str] = None
    vulnerabilities: List[VulnerabilityIssue] = []
    security_score: Optional[int] = None # 0 to 100

    class Config:
        populate_by_name = True
