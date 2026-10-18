from fastapi import APIRouter
from pydantic import BaseModel
from backend.modules.evidence_ledger import EvidenceLedger

router = APIRouter(prefix="/api/evidence", tags=["evidence"])
ledger = EvidenceLedger()


class RecordRequest(BaseModel):
    email_hash: str
    case_id: str


class VerifyRequest(BaseModel):
    evidence_id: str
    body: str


@router.post("/record")
def record_evidence(req: RecordRequest):
    """Lock an email hash into the ledger"""
    return ledger.record_evidence(req.email_hash, req.case_id)


@router.get("/chain")
def check_chain():
    """Verify the whole ledger has not been altered"""
    return ledger.verify_chain()


@router.post("/verify")
def verify_evidence(req: VerifyRequest):
    """Re-hash the email and compare it with the ledger (Integrity Check)"""
    return ledger.verify_evidence(req.evidence_id, req.body)
