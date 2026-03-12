from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Optional
from datetime import datetime

class ScanRequest(BaseModel):
    target: str

class ScanResult(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    target: str
    status: str  # running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    raw_output: Dict[str, str] = {}  # {"nmap": "...", "nikto": "...", etc.}

    model_config = ConfigDict(populate_by_name=True)
