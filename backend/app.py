from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from backend.config import get_db_connection, FASTAPI_HOST, FASTAPI_PORT
from backend.modules.extraction import DataExtractor
from backend.utils.eml_parser import EMLParser
from pydantic import BaseModel
from typing import Optional, List
import os

app = FastAPI(title="Machine Minds - SIH 2026", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = get_db_connection()

class EmailInput(BaseModel):
    sender: Optional[str] = None
    receiver: Optional[str] = None
    date: Optional[str] = None
    subject: Optional[str] = None
    body: str
    label: int = 0

class ExtractionResponse(BaseModel):
    sender: Optional[str]
    subject: Optional[str]
    ioc_count: int
    iocs: List[dict]
    email_hash: str

@app.get("/")
async def health():
    return {
        "status": "ok",
        "app": "Machine Minds SIH 2026",
        "module": "Data Extraction (Module 1)"
    }

@app.post("/api/extract")
async def extract_email(email: EmailInput) -> ExtractionResponse:
    """Extract IOCs from a single email (JSON)"""
    try:
        extracted = DataExtractor.extract_email(
            sender=email.sender,
            receiver=email.receiver,
            date=email.date,
            subject=email.subject,
            body=email.body,
            dataset_source="api",
            label=email.label
        )
        
        return ExtractionResponse(
            sender=extracted.sender,
            subject=extracted.subject,
            ioc_count=len(extracted.iocs),
            iocs=[{
                'value': ioc.value,
                'type': ioc.ioc_type,
                'source': ioc.source
            } for ioc in extracted.iocs],
            email_hash=extracted.email_hash
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/extract-eml")
async def extract_eml(file: UploadFile = File(...)):
    """Extract IOCs from uploaded .eml file"""
    try:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        email_dict = EMLParser.parse_eml_file(temp_path)
        
        extracted = DataExtractor.extract_email(
            sender=email_dict.get('sender'),
            receiver=email_dict.get('receiver'),
            date=email_dict.get('date'),
            subject=email_dict.get('subject'),
            body=email_dict.get('body', ''),
            dataset_source="eml_upload",
            label=0
        )
        
        os.remove(temp_path)
        
        return {
            "status": "success",
            "file": file.filename,
            "sender": extracted.sender,
            "receiver": extracted.receiver,
            "subject": extracted.subject,
            "ioc_count": len(extracted.iocs),
            "iocs": [{
                'value': ioc.value,
                'type': ioc.ioc_type,
                'source': ioc.source
            } for ioc in extracted.iocs],
            "email_hash": extracted.email_hash,
            "extraction_timestamp": extracted.extraction_timestamp
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get extraction statistics from database"""
    collection = db['extracted_emails']
    total = collection.count_documents({})
    
    total_iocs = 0
    for doc in collection.find({}, {'iocs': 1}):
        total_iocs += len(doc.get('iocs', []))
    
    return {
        "total_emails": total,
        "total_iocs": total_iocs,
        "avg_iocs_per_email": total_iocs / total if total > 0 else 0,
        "module_status": "Module 1: Data Extraction ✅ COMPLETE"
    }

@app.get("/api/emails")
async def get_emails(dataset: Optional[str] = None, limit: int = 10):
    """Get extracted emails from database"""
    collection = db['extracted_emails']
    
    query = {}
    if dataset:
        query['dataset_source'] = dataset
    
    emails = list(collection.find(query).limit(limit))
    
    for email in emails:
        email['_id'] = str(email['_id'])
    
    return emails

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=FASTAPI_HOST, port=FASTAPI_PORT, reload=FASTAPI_RELOAD)
