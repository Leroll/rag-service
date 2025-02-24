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


class LegacyQueryRequest(BaseModel):
    """兼容老的请求参数格式 与 当下请求参数格式
    """
    # 老的
    um: str  # 请求um
    query_mode: str = 'v'  # 看到请求参数为v，意义不明 
    request_id: str # 请求id
    session_id: str # 会话id
    max_length: int = 512
    top_p: float = 0.7  # 生成文本的概率
    temperature: float = 0.95  # 生成文本的温度
    kdb1: int = 1  # 看到请求参数为0，意义不明
    kdb2: int = 1  # 看到请求参数为0，意义不明
    kdb3: int = 1  # 看到请求参数为0，意义不明
    
    # 当下的
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
@app.post("/query/full", response_model=Response)
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


# SSE流式输出路由
@app.post("/query/stream")
async def query_endpoint(request: QueryRequest) -> StreamingResponse:
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
                async for chunk in resp:
                    # SSE格式要求每行以 "data: " 开头并以双换行符结束
                    # yield f"data: {chunk}\n\n"
                    yield chunk
            else:
                # 如果不是流式结果，直接返回完整结果
                # yield f"data: {resp}\n\n"
                yield str(resp)
                
            # 发送结束信号
            # yield "data: [DONE]\n\n"
                
        except Exception as e:
            # 错误处理
            yield f"data: ERROR: {str(e)}\n\n"

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
async def query_endpoint_legacy(request: LegacyQueryRequest) -> StreamingResponse:
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
                async for chunk in resp:
                    # SSE格式要求每行以 "data: " 开头并以双换行符结束
                    # yield f"data: {chunk}\n\n"
                    res = {"answer": chunk, "code": 200}
                    yield str(res)
            else:
                # 如果不是流式结果，直接返回完整结果
                # yield f"data: {resp}\n\n"
                res = {"answer": str(resp), "code":200}
                yield res
                
            # 发送结束信号, 历史接口中在for循环结束后，有一个 code=201 的返回
            res['code'] = 201
            yield str(res)
                
        except Exception as e:
            # 错误处理
            yield {"answer": f"ERROR: {str(e)}\n\n", "code": 102}

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
async def insert_endpoint(request: InsertRequest):
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: rag.insert(request.text))
        return Response(status="success", message="Text inserted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# insert by file
@app.post("/insert_file", response_model=Response)
async def insert_file(file: UploadFile = File(...)):
    """
    处理上传的文件并插入到LightRAG，支持多种文件类型（包括Excel、PDF、DOCX等）
    """
    try:
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

        return Response(
            status="success",
            message=f"成功处理文件 {file.filename} 并插入内容"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理文件 {file.filename} 时出错: {str(e)}"
        )



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
    
    uvicorn.run(app, host=cfg.rag_server.host, port=cfg.rag_server.port)
