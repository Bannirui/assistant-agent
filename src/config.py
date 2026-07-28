import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    dashscope_embedding_model: str = "text-embedding-v3"

    copilot_env: str = "development"
    copilot_log_level: str = "DEBUG"
    copilot_max_agent_iterations: int = 10

    copilot_data_dir: str = "./data"
    copilot_sop_dir: str = "./data/sop"
    copilot_knowledge_dir: str = "./data/knowledge"
    copilot_qdrant_path: str = "./data/qdrant"

    copilot_host: str = "0.0.0.0"
    copilot_port: int = 8000

    @property
    def sop_path(self) -> Path:
        return Path(self.copilot_sop_dir)

    @property
    def knowledge_path(self) -> Path:
        return Path(self.copilot_knowledge_dir)

    @property
    def qdrant_path(self) -> Path:
        return Path(self.copilot_qdrant_path)

    @property
    def data_path(self) -> Path:
        return Path(self.copilot_data_dir)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
