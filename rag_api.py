from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import os
from lightrag import QueryParam
from typing import Optional
import asyncio
import nest_asyncio
import aiofiles
from file_processing import file_processing
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import inspect
from fastapi.middleware.cors import CORSMiddleware
import json
import traceback
from loguru import logger
from config import cfg
from lightrag_factory import RAGFactory

# 日志及其他配置
nest_asyncio.apply()  # Apply nest_asyncio to solve event loop issues
os.environ["TIKTOKEN_CACHE_DIR"] = cfg.tiktoken.cache_dir
def logger_filter(record: dict) -> bool:
    """日志过滤器，只记录指定模块的日志
    """
    filter_modules = ["rag_api", "file_processing", "lightrag_factory"]
    flag = False
    for module in filter_modules:
        if module in record["module"]:
            flag = True
            break
    return flag
logger.add(cfg.rag_api.log_path, 
           rotation=cfg.rag_api.log_rotation, 
           level=cfg.rag_api.log_level,
           filter=logger_filter, 
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {module} | {function}:{line} | {message}",
           )

# LightRAG实例
rag = RAGFactory.get_instance() 

# FastAPI app
app = FastAPI(title="RAG-service", description="API for RAG operations")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
) # 增加跨域支持 


# Data models
class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid"
    only_need_context: bool = False


class LegacyQueryRequest(BaseModel):
    """兼容老的请求参数格式 与 当下请求参数格式
    """
    # 老的
    um: str  # 请求um
    request_id: str # 请求id
    session_id: str # 会话id
    query_mode: str = 'v'  # 看到请求参数为v，意义不明 
    
    # 当下的
    query: str
    mode: str = "naive"  # 暂时默认为naive, 
                          # naive 的时候就不是异步生成器了，需要进一步检查 #TODO
                          # 但是mix, hybrid的效果不好，需要进一步调整
    only_need_context: bool = False


class InsertRequest(BaseModel):
    text: str


class Response(BaseModel):
    status: str
    data: Optional[str] = None
    message: Optional[str] = None


# API routes
@app.post("/query/full", response_model=Response)
async def query_full(request: QueryRequest):
    try:
        logger.info(f"IN | {request.model_dump()}")
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
        response = Response(status="success", data=result)
        logger.info(f"OUT | {response.model_dump()}")
        return response
    except Exception as e:
        resp = Response(status="error", message=traceback.format_exc())
        logger.error(f"OUT | {resp.model_dump()}")
        return resp
    

# 流式查询
@app.post("/v1/query")
async def v1_query_legacy(request: LegacyQueryRequest) -> StreamingResponse:
    """流式接口，直接流式返回答案，不做json包装，且不是SSE协议
    """
    logger.info(f"IN | {request.model_dump()}")
    
    async def stream_results() -> AsyncGenerator[str, None]:
        try:        
            query_param = QueryParam(
                mode=request.mode, 
                only_need_context=request.only_need_context,
                stream=True  # 启用流式输出
            )
        
            resp = rag.query(request.query, param=query_param)
            
            is_stream = inspect.isasyncgen(resp)  # 检查是否为异步生成器
            if is_stream:  # 检查是否为异步生成器
                total = ""
                async for chunk in resp:  # 流式处理异步生成器返回的结果
                    total += chunk
                    yield chunk  # 流式返回时，fastapi不会自动转换为json格式，这里是纯字符串返回
            else:
                total = resp
                yield resp  # 直接返回结果
                
            logger.info(f"OUT | is_asyncgen: {is_stream} | {total}")
                
        except Exception as e:
            res = f"ERROR: {traceback.format_exc()}"
            logger.error(f"OUT | {res}")
            yield json.dumps(res, ensure_ascii=False)
            
    return StreamingResponse(
        stream_results(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
        }
    )


# insert by text
@app.post("/insert", response_model=Response)
async def insert(request: InsertRequest):
    try:
        logger.info(f"IN | {request.model_dump()}")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: rag.insert(request.text))
        resp = Response(status="success", message="Text inserted successfully")
        logger.info(f"OUT | {resp.model_dump()}")
        return resp
    except Exception as e:
        resp = Response(status="error", message=traceback.format_exc())
        logger.error(f"OUT | {resp.model_dump()}")
        return resp


# insert by file
@app.post("/insert_file", response_model=Response)
async def insert_file(file: UploadFile = File(...)):
    """
    处理上传的文件并插入到LightRAG，支持多种文件类型（包括Excel、PDF、DOCX等）
    """
    try:
        logger.info(f"IN | {file.filename}")
        
        # 1. 获取文件信息
        file_content = await file.read()  # 读取文件内容（字节流）
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''  # 获取文件扩展名
        
        # 2. 对文件进行处理
        content, msg = file_processing(file_content, file_extension)   
        if content is None:
            raise Exception(f"处理文件 {file.filename} 时出错: {msg}")
             
        # 3. 异步插入内容到 LightRAG
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: rag.insert(content))

        resp = Response(
            status="success",
            message=f"成功处理文件 {file.filename} 并插入内容"
        )
        logger.info(f"OUT | {resp.model_dump()}")
        return resp

    except Exception as e:
        resp = Response(
            status="error",
            message=f"处理文件 {file.filename} 时出错: {e}"
        )
        logger.error(f"OUT | {resp.model_dump()}")
        return resp


@app.get("/health")
async def health_check():
    resp = {"status": "healthy"}
    logger.info(f"OUT | {resp}")
    return resp


@app.get("/version", response_model=Response)
async def get_version():
    try:
        resp = Response(status="success", data=cfg.version, message="Version retrieved successfully")
        logger.info(f"OUT | {resp.model_dump()}")
        return resp
    except Exception as e:
        resp = Response(status="error", message=traceback.format_exc())
        logger.error(f"OUT | {resp.model_dump()}")
        return resp
