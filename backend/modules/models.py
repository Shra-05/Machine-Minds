from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class IOCModel:
    """Indicator of Compromise stored in MongoDB"""
    value: str
    ioc_type: str
    source: str
    extracted_at: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class EmailModel:
    """Email document stored in MongoDB"""
    sender: Optional[str]
    receiver: Optional[str]
    date: Optional[str]
    subject: Optional[str]
    body: str
    iocs: List[dict]
    email_hash: str
    extraction_timestamp: str
    dataset_source: str
    original_label: int
    confidence: float
    status: str = "extracted"
    threat_score: float = 0.0
    _id: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)
