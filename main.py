from fastapi import FastAPI, Header, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.pipeline import run_pipeline
from fastapi.openapi.utils import get_openapi
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

TEAM_TOKEN = "87436cd7e9ec09c6ae1c66eb55aa5da937d1ec6c22a032731eb773c9a9727777"

class RequestData(BaseModel):
    documents: str
    questions: list[str]

@app.post("/hackrx/run")
async def process_query(data: RequestData, Authorization: Optional[str] = Header(None)):
    logger.info(f"Incoming request: {data.dict()}")
    logger.info(f"Authorization header: {Authorization}")
    
    if Authorization != f"Bearer {TEAM_TOKEN}":
        logger.error("Invalid or missing token")
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    
    try:
        result = run_pipeline(data.documents, data.questions)
        logger.info(f"Response generated: {result}")
        return result
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    logger.info("Health check accessed")
    return {"status": "healthy"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="HackRx LLM Query API",
        version="1.0.0",
        description="Send document + questions and get answers using LLM-powered retrieval",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi