#!/usr/bin/env python3
"""
Simple RAG API - FastAPI wrapper for frontend integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from rag.simple_rag import SimpleRAG

app = FastAPI(title="RAG API", description="Simple RAG pipeline API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize RAG
rag = SimpleRAG()

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class QueryResponse(BaseModel):
    question: str
    restructured_question: str
    answer: str
    context: List[str]

@app.get("/")
def read_root():
    return {"message": "RAG API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "collection": "documents"}

@app.post("/query", response_model=QueryResponse)
def query_document(request: QueryRequest):
    try:
        result = rag.query(request.question, request.top_k)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
def upload_document(json_file: str):
    try:
        rag.load_and_store(json_file)
        return {"message": "Document uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
