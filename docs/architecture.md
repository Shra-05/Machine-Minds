# TrustMail Architecture

## System Flow
Raw Email → Data Extraction → Multi-Layer Analysis → Threat Detection → Forensic Investigation → Evidence Collection

## Components

### 1. Data Extraction
- Email headers, body, subject parsing
- URL, domain, attachment extraction
- Metadata extraction (sender, recipients, timestamps)

### 2. Multi-Layer Threat Analysis
- **Content Analysis:** Phishing language detection
- **Header Analysis:** SPF/DKIM/DMARC validation
- **IOC Analysis:** URL/Domain reputation lookup

### 3. Risk Score Engine
- Ensemble model combining all signals
- Confidence scoring (0.0 - 1.0)
- Classification: PHISHING | SUSPICIOUS | LEGITIMATE

### 4. Forensic Investigation
- Email hop analysis (route tracing)
- Geolocation mapping of source
- Threat correlation with campaigns
- IOC database lookup

### 5. Evidence Collection
- SHA-256 hash generation
- Blockchain immutable logging
- Chain of custody support

### 6. Dashboard
- Real-time risk scores
- Geolocation maps
- Forensic reports
- Email traces

## Tech Stack
- **Backend:** FastAPI + Python
- **ML:** Scikit-learn + XGBoost + SHAP
- **Database:** MongoDB + Neo4j
- **Blockchain:** Hyperledger Fabric
- **Frontend:** React + Vite
- **Deployment:** Docker + Kubernetes
