from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import os
from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_embed, ollama_model_complete
from lightrag.utils import EmbeddingFunc
from typing import Optional
import asyncio
import nest_asyncio
import aiofiles

from config import cfg
nest_asyncio.apply()  # Apply nest_asyncio to solve event loop issues


app = FastAPI(title="RAG-service", description="API for RAG operations")

# Configure working directory
print(f"working_dir: {cfg.file.working_dir}")
if not os.path.exists(cfg.file.working_dir):
    os.mkdir(cfg.file.working_dir)

rag = LightRAG(
    working_dir=cfg.file.working_dir,
    llm_model_func=ollama_model_complete,
    llm_model_name=cfg.llm.model_name,
    llm_model_max_async=cfg.llm.llm_model_max_async,
    llm_model_max_token_size=cfg.llm.llm_model_max_token_size,
    llm_model_kwargs={"host": cfg.llm.model_host, "options": {"num_ctx": cfg.llm.num_ctx}},
    embedding_func=EmbeddingFunc(
        embedding_dim=cfg.embed.embed_dim,
        max_token_size=cfg.embed.embed_max_token_size,
        func=lambda texts: ollama_embed(
            texts, embed_model=cfg.embed.embed_model, host=cfg.embed.embed_host
        ),
    ),
)

# Data models
class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid"
    only_need_context: bool = False


class InsertRequest(BaseModel):
    text: str


class Response(BaseModel):
    status: str
    data: Optional[str] = None
    message: Optional[str] = None


# API routes
@app.post("/query", response_model=Response)
async def query_endpoint(request: QueryRequest):
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: rag.query(
                request.query,
                param=QueryParam(
                    mode=request.mode, only_need_context=request.only_need_context
                ),
            ),
        )
        return Response(status="success", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# insert by text
@app.post("/insert", response_model=Response)
async def insert_endpoint(request: InsertRequest):
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: rag.insert(request.text))
        return Response(status="success", message="Text inserted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# insert by file in payload
@app.post("/insert_file", response_model=Response)
async def insert_file(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        # Read file content
        try:
            content = file_content.decode("utf-8")
        except UnicodeDecodeError:
            # If UTF-8 decoding fails, try other encodings
            content = file_content.decode("gbk")
        # Insert file content
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: rag.insert(content))

        return Response(
            status="success",
            message=f"File content from {file.filename} inserted successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/version", response_model=Response)
async def get_version():
    try:
        return Response(status="success", data=cfg.version, message="Version retrieved successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8020)

# Usage example
# To run the server, use the following command in your terminal:
# python lightrag_api_openai_compatible_demo.py

# Example requests:
# 1. Query:
# curl -X POST "http://127.0.0.1:8020/query" -H "Content-Type: application/json" -d '{"query": "your query here", "mode": "hybrid"}'

# 2. Insert text:
# curl -X POST "http://127.0.0.1:8020/insert" -H "Content-Type: application/json" -d '{"text": "your text here"}'

# 3. Insert file:
# curl -X POST "http://127.0.0.1:8020/insert_file" -H "Content-Type: multipart/form-data" -F "file=@path/to/your/file.txt"

# 4. Health check:
# curl -X GET "http://127.0.0.1:8020/health"
