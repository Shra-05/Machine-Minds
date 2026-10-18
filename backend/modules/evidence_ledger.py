import hashlib
import json
from datetime import datetime, timezone
from pymongo import ASCENDING
from backend.config import get_db_connection

GENESIS_HASH = "0" * 64


def _block_hash(fields: dict) -> str:
    # Sort keys so the same data always produces the same hash
    payload = json.dumps(fields, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class EvidenceLedger:
    def __init__(self):
        self.db = get_db_connection()
        self.col = self.db["evidence_ledger"]
        self.col.create_index([("sequence", ASCENDING)], unique=True)

    def record_evidence(self, email_hash: str, case_id: str) -> dict:
        last = self.col.find_one(sort=[("sequence", -1)])
        seq = last["sequence"] + 1 if last else 1
        prev_hash = last["block_hash"] if last else GENESIS_HASH

        fields = {
            "sequence": seq,
            "evidence_id": f"EV-{seq:06d}",
            "email_hash": email_hash,
            "case_id": case_id,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "prev_hash": prev_hash,
        }
        block = {**fields, "block_hash": _block_hash(fields)}
        self.col.insert_one(block)
        block.pop("_id", None)  # Mongo adds _id; remove it before returning
        return block

    def verify_chain(self) -> dict:
        expected_seq = 1
        expected_prev = GENESIS_HASH
        for block in self.col.find({}, {"_id": 0}).sort("sequence", ASCENDING):
            if block["sequence"] != expected_seq or block["prev_hash"] != expected_prev:
                return {"valid": False, "broken_at": block["sequence"], "reason": "chain link broken"}
            fields = {k: v for k, v in block.items() if k != "block_hash"}
            if _block_hash(fields) != block["block_hash"]:
                return {"valid": False, "broken_at": block["sequence"], "reason": "record contents altered"}
            expected_prev = block["block_hash"]
            expected_seq += 1
        return {"valid": True, "blocks_checked": expected_seq - 1}

    def verify_evidence(self, evidence_id: str, body_text: str) -> dict:
        block = self.col.find_one({"evidence_id": evidence_id}, {"_id": 0})
        if not block:
            return {"status": "NOT_FOUND", "evidence_id": evidence_id}

        # Same hashing rule as Module 1: SHA256 of the body text
        current_hash = hashlib.sha256((body_text or "").encode("utf-8")).hexdigest()
        chain = self.verify_chain()
        intact = current_hash == block["email_hash"] and chain["valid"]

        return {
            "evidence_id": evidence_id,
            "status": "INTACT" if intact else "TAMPERED",
            "stored_hash": block["email_hash"],
            "current_hash": current_hash,
            "chain_valid": chain["valid"],
        }
