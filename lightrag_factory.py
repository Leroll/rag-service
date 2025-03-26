from lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
from lightrag.llm.ollama import ollama_embed, ollama_model_complete
from loguru import logger
from typing import Any, Optional
from config import cfg
import os


class NaiveLightRAG(LightRAG):
    """仅使用naive模式时，置空实体抽取等调用大模型的方法，提高raw_docs生成rag库的速度
    """
    async def _process_entity_relation_graph(self, chunk: dict[str, Any]) -> None:
        pass

class RAGFactory:
    _instance: Optional[LightRAG] = None
    
    @staticmethod
    def get_lightrag_class():
        """根据配置的mode返回对应的LightRAG类
        """
        mode = cfg.scene.mode.value
        if mode == 'default':
            return LightRAG
        elif mode == 'naive':
            return NaiveLightRAG
        else:
            raise ValueError(f"Unsupported mode: {mode}")
    
    @classmethod
    def _create_rag(cls) -> LightRAG:
        """创建并返回LightRAG实例
        """
        logger.info("Creating LightRAG instance...")
        
        # lightRAG类
        lightrag_class = cls.get_lightrag_class()
        logger.info(f"lightRAG_class: {lightrag_class.__name__}")
        
        # rag库路径
        rag_path = cfg.scene.path + '/rag'
        logger.info(f"rag_path: {rag_path}")
        if not os.path.exists(rag_path):
            os.mkdir(rag_path)

        rag = lightrag_class(
            working_dir=rag_path,
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
        return rag
    
    @classmethod
    def get_instance(cls) -> LightRAG:
        """获取单例RAG实例"""
        if cls._instance is None:
            cls._instance = cls._create_rag()
        return cls._instance    

if __name__ == '__main__':
    rag = RAGFactory.get_instance()
    print(rag)
