from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.threat_detection import analyze_email
import uvicorn

app = FastAPI(
    title="TrustMail - Email Threat Detection API",
    description="AI-powered phishing detection and forensic investigation platform"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-email")
async def analyze(file: UploadFile = File(...)):
    try:
        email_content = await file.read()
        email_text = email_content.decode('utf-8', errors='ignore')
        result = analyze_email(email_text)
        return {
            "status": "success",
            "risk_score": result['risk_score'],
            "classification": result['classification'],
            "indicators": result['indicators'],
            "geolocation": result['geolocation'],
            "forensic_readiness": True
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
def health_check():
    return {
        "status": "TrustMail API is running",
        "version": "1.0.0",
        "components": ["threat_detection", "geolocation_mapping", "forensic_logging"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
