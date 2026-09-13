import os

class Settings:
    APP_NAME = "TrustMail"
    APP_VERSION = "1.0.0"
    API_PORT = 8000
    DEBUG = True
    
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    DB_NAME = "trustmail"
    
    FABRIC_CONFIG = {
        "channel": "trustmail",
        "chaincode": "evidence-logging"
    }

settings = Settings()
