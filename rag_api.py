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
import textract
import tempfile
import openpyxl
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import inspect
from fastapi.middleware.cors import CORSMiddleware
import json
import traceback
from loguru import logger
from config import cfg

# 设置
nest_asyncio.apply()  # Apply nest_asyncio to solve event loop issues
os.environ["TIKTOKEN_CACHE_DIR"] = cfg.tiktoken.cache_dir
logger.add(cfg.rag_api.log_path, 
           rotation=cfg.rag_api.log_rotation, 
           level=cfg.rag_api.log_level,
           filter="rag_api", 
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {module} | {function} | {line} - {message}",
           )


# FastAPI app
app = FastAPI(title="RAG-service", description="API for RAG operations")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
) # 增加跨域支持 

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
    log_file_path=os.path.join(os.path.dirname(cfg.rag_api.log_path), "lightrag.log"),
    log_level=cfg.rag_api.log_level,
)

# Data models
class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid"
    only_need_context: bool = False


class LegacyQueryRequest(BaseModel):
    """兼容老的请求参数格式 与 当下请求参数格式
    """
    # 老的
    request_id: str # 请求id
    session_id: str # 会话id
    um: str  # 请求um
    query_mode: str = 'v'  # 看到请求参数为v，意义不明 
    
    # 当下的
    query: str
    mode: str = "naive"  # 暂时默认为naive
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


# SSE流式输出路由
# 更改了SSE的输出格式，不再以 "data: " 开头，而是直接返回json格式的数据
@app.post("/query/stream")
async def query_stream(request: QueryRequest) -> StreamingResponse:
    logger.info(f"IN | {request.model_dump()}")
    
    async def stream_results() -> AsyncGenerator[str, None]:
        try:
            # 创建查询参数
            query_param = QueryParam(
                mode=request.mode, 
                only_need_context=request.only_need_context,
                stream=True  # 启用流式输出
            )
            
            # 执行查询
            resp = rag.query(request.query, param=query_param)
            
            # 检查是否为异步生成器
            if inspect.isasyncgen(resp):
                # 流式处理异步生成器返回的结果
                res = ""
                async for chunk in resp:
                    # SSE格式要求每行以 "data: " 开头并以双换行符结束
                    # yield f"data: {chunk}\n\n"
                    res += chunk
                    yield chunk
            else:
                # 如果不是流式结果，直接返回完整结果
                res = json.dumps(resp, ensure_ascii=False)
                yield res
                
            # 发送结束信号
            # yield "data: [DONE]\n\n"
            logger.info(f"OUT | {res}")
                
        except Exception as e:
            # 错误处理
            msg = f"data: ERROR: {traceback.format_exc()}\n\n"
            logger.error(f"OUT | {msg}")
            yield json.dumps(msg, ensure_ascii=False)

    # 返回StreamingResponse，指定SSE的media_type
    return StreamingResponse(
        stream_results(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
        }
    )
    

# SSE流式输出路由 - 兼容老接口
@app.post("/v1/query")
async def v1_query_legacy(request: LegacyQueryRequest) -> StreamingResponse:
    """对齐老项目的流式接口
    
    该接口流式回复的时候是，累加的，即每次返回的结果都是上一次的结果加上这次的结果
    并且回复格式是 {answer: str, code: int}，其中 code=200 表示正常回复，code=201 表示结束
    """
    async def stream_results() -> AsyncGenerator[str, None]:
        try:
            logger.info(f"IN | {request.model_dump()}")
            
            query_param = QueryParam(
                mode=request.mode, 
                only_need_context=request.only_need_context,
                stream=True  # 启用流式输出
            ) # 创建查询参数
            resp = rag.query(request.query, param=query_param)
            
            
            if inspect.isasyncgen(resp):  # 检查是否为异步生成器
                chunk_all = ""
                async for chunk in resp:  # 流式处理异步生成器返回的结果
                    chunk_all += chunk
                    res = {"answer": chunk_all, "code": 200}
                    yield json.dumps(res, ensure_ascii=False)  # 流式返回时，fastapi不会自动转换为json格式，需手动
            else:
                res = {"answer": str(resp), "code":200}  
                yield json.dumps(res, ensure_ascii=False)
                
            # 发送结束信号, 历史接口中在for循环结束后，有一个 code=201 的返回
            logger.info(f"OUT | {res}")
            res['code'] = 201
            yield json.dumps(res, ensure_ascii=False)
                
        except Exception as e:
            res = {"answer": f"ERROR: {traceback.format_exc()}\n\n", "code": 102}
            logger.error(f"OUT | {res}")
            yield json.dumps(res, ensure_ascii=False)

    # 返回StreamingResponse，指定SSE的media_type
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
        # 读取文件内容（字节流）
        file_content = await file.read()
        
        # 获取文件扩展名
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        
        # 处理 Excel 文件 (.xlsx)
        if file_extension == 'xlsx':
            try:
                # 创建临时文件来存储上传的字节内容
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name
                
                # 使用 openpyxl 读取 Excel 文件
                workbook = openpyxl.load_workbook(temp_file_path)
                content = ""
                for sheet in workbook.sheetnames:
                    worksheet = workbook[sheet]
                    for row in worksheet.rows:
                        for cell in row:
                            cell_value = cell.value
                            if cell_value is not None:
                                content += str(cell_value) + " "
                
                # 删除临时文件
                os.unlink(temp_file_path)
                
            except Exception as excel_error:
                raise HTTPException(
                    status_code=400,
                    detail=f"处理 Excel 文件 {file.filename} 失败: {str(excel_error)}"
                )
        
        # 处理其他文件类型（如 PDF、DOCX、PPTX 等）
        else:
            try:
                # 创建临时文件来存储上传的字节内容
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name
                
                # 使用 textract 提取内容
                text_content = textract.process(temp_file_path)
                content = text_content.decode('utf-8')
                
                # 删除临时文件
                os.unlink(temp_file_path)
                
            except Exception as textract_error:
                # 如果 textract 处理失败，尝试直接解码（适用于纯文本文件）
                try:
                    content = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    # 尝试使用 GBK 编码（常见于中文文档）
                    try:
                        content = file_content.decode('gbk')
                    except UnicodeDecodeError:
                        raise HTTPException(
                            status_code=400,
                            detail="无法解码文件内容，请确保文件格式受支持"
                        )

        # 异步插入内容到 LightRAG
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
            message=f"处理文件 {file.filename} 时出错: {traceback.format_exc()}"
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
