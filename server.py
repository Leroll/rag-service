import uvicorn
from loguru import logger
import logging
from typing import Dict, Any

class InterceptHandler(logging.Handler):
    """将标准 logging 日志转发到 Loguru"""
    
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info
        ).log(level, record.getMessage())

# 配置日志拦截 ----------------------------------------------------
logging.basicConfig(handlers=[InterceptHandler()], level=0)

# 强制 Uvicorn 日志传播到根日志器
for logger_name in logging.root.manager.loggerDict:
    if logger_name.startswith("uvicorn"):
        logging.getLogger(logger_name).handlers = []
        logging.getLogger(logger_name).propagate = True

# 配置 Loguru ----------------------------------------------------
from config import cfg
from rag_api import app

logger.add(
    cfg.server.log_path,
    rotation=cfg.server.log_rotation,
    level=cfg.server.log_level,
    enqueue=True,
    backtrace=True,
    encoding="utf-8",
    filter="uvicorn",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {module} | {function}:{line} | {message}",
)

# 启动服务 -------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        app,
        host=cfg.server.host,
        port=cfg.server.port,
        log_config=None  # 禁用 Uvicorn 自有日志配置
    )