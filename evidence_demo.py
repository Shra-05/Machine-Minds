import hashlib
from backend.config import get_db_connection
from backend.modules.evidence_ledger import EvidenceLedger

ledger = EvidenceLedger()
db = get_db_connection()
emails = db["extracted_emails"]

body = "Urgent: verify your account at https://secure-bank-verify.com/login"
email_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
test_id = emails.insert_one({"subject": "DEMO", "body": body, "email_hash": email_hash}).inserted_id

print("\n1. Recording evidence in the ledger...")
rec = ledger.record_evidence(email_hash, case_id="CASE-DEMO-001")
print("   evidence_id:", rec["evidence_id"])
print("   block_hash: ", rec["block_hash"][:24] + "...")

print("\n2. Integrity check on the untouched email...")
print("  ", ledger.verify_evidence(rec["evidence_id"], body))

print("\n3. Attacker edits the email body...")
print("  ", ledger.verify_evidence(rec["evidence_id"], body.replace("verify", "confirm")))

print("\n4. Attacker alters a ledger record...")
ledger.col.update_one({"evidence_id": rec["evidence_id"]}, {"$set": {"case_id": "CASE-FAKE"}})
print("  ", ledger.verify_chain())
ledger.col.update_one({"evidence_id": rec["evidence_id"]}, {"$set": {"case_id": "CASE-DEMO-001"}})
print("   Restored:", ledger.verify_chain())

emails.delete_one({"_id": test_id})
print("\nDemo complete.\n")
