import yaml
import os
from pydantic import BaseModel
from utils import Singleton  # 假设 utils 中有 Singleton 实现


class EmbedConfig(BaseModel):
    """嵌入模型相关配置"""
    embed_model: str = "nomic-embed-text"
    embed_host: str = "http://localhost:11434"
    embed_dim: int = 768
    embed_max_token_size: int = 8192


class LLMConfig(BaseModel):
    """LLM 模型相关配置"""
    model_name: str = "deepseek-r1:7b"
    model_host: str = "http://localhost:11434"
    num_ctx: int = 8192
    llm_model_max_token_size: int = 8192
    llm_model_max_async: int = 4

    
class TikToken(BaseModel):
    cache_dir: str = "resources/tiktok"


class SceneConfig(BaseModel):
    """场景相关配置"""
    path: str = "resources/scenes/identity" 
    
class RagApi(BaseModel):
    """rag服务相关"""
    log_path: str = "logs/rag_api.log"
    log_level: str = "INFO"
    log_rotation: str = "10 MB"

class ServerConfig(BaseModel):
    """服务相关配置"""
    host: str = "0.0.0.0"
    port: int = 50051
    log_path: str = "logs/server.log"
    log_level: str = "INFO"
    log_rotation: str = "10 MB"

    
class ConfigData(BaseModel):
    """整体配置"""
    embed: EmbedConfig
    llm: LLMConfig
    scene: SceneConfig
    rag_api: RagApi
    tiktoken: TikToken
    server: ServerConfig
    version: str


@Singleton
class Config(object):
    def __init__(self, conf_path='config'):
        self.env = self.__init_env()
        self.config = self.__init_config(conf_path)

    def yaml_load(self, path):
        with open(path, "r", encoding="utf-8") as fin:
            return yaml.load(fin, Loader=yaml.FullLoader)

    def __init_env(self) -> str:
        env = os.getenv("env_profile", "prod")
        print(f"Env is {env}")
        return env

    def __init_config(self, conf_path: str) -> ConfigData:
        """从环境变量 env_profile 中获取环境名称并加载配置

        Args:
            conf_path (str): 配置文件夹路径

        Returns:
            ConfigData: Pydantic 验证后的配置对象
        """
        config_path = f'{conf_path}/{self.env}.yaml'
        try:
            config_dict = self.yaml_load(config_path)
            config = ConfigData(**config_dict)
        except FileNotFoundError:
            print(f"Config file {config_path} not found, using default values")
            config = ConfigData(embed=EmbedConfig(), llm=LLMConfig(), scene=SceneConfig(), rag_server=RagServer())
        return config

    def get_config(self):
        return self.config


# 初始化配置
cfg = Config('./config').get_config()

if __name__ == "__main__":
    cfg = Config('./config')
    print(cfg.env)
    
    cfg = cfg.get_config()
    print(cfg)
    print(cfg.embed.embed_model)
    print(cfg.scene.path)
    print(cfg.version)