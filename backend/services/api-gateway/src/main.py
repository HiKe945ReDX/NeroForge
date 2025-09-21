import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
import requests
import uvicorn

app = FastAPI(title="Guidora API Gateway", version="1.0.0")

# Service map
SERVICES = {
    "ai": "http://ai-guidance:5001",
    "careers": "http://career-atlas:5002", 
    "gamification": "http://gamification:5003",
    "simulation": "http://simulation-service:5004",
    "portfolio": "http://portfolio-service:5005",
    "users": "http://user-service:5007",
    "interviews": "http://localhost:5008",
    "notifications": "http://localhost:5009"
}

@app.get("/")
async def root():
    return {
        "service": "Guidora API Gateway",
        "status": "working",
        "version": "1.0.0",
        "services": len(SERVICES)
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "services": SERVICES}

@app.get("/api/{service_name}")
@app.get("/api/{service_name}/{path:path}")
async def proxy_request(service_name: str, path: str = ""):
    if service_name not in SERVICES:
        return {"error": f"Service {service_name} not found"}
    
    try:
        url = f"{SERVICES[service_name]}/{path}"
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e), "service": service_name}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
