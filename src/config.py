from pathlib import Path
from pydantic_settings import BaseSettings


# 启动后自动读取配置然后覆盖类的默认值 配置加载优先级 环境变量>.env文件>类字段默认值
class Settings(BaseSettings):
    # LLM大模型
    # 供应商标识 deepseek/openai/qwen
    llm_provider: str = ""
    # 下面3个是模型的必填参数 不用默认值 强制让py校验必填
    # 模型名称 deepseek-chat/gpt-4o
    llm_model: str
    # API密钥
    llm_api_key: str
    # API地址
    llm_base_url: str

    # 向量模型
    # 供应商标识 dashscope/openai/local
    embed_provider: str = ""
    # 下面3个是模型的必填参数 不用默认值 强制让py校验必填
    # 模型名称
    embed_model: str
    # API密钥
    embed_api_key: str
    # API地址
    embed_base_url: str

    # 应用配置
    # 运行环境
    copilot_env: str = "development"
    # 日志级别
    copilot_log_level: str = "DEBUG"
    # Agent最大工具调用轮数
    copilot_max_agent_iterations: int = 10

    # 数据路径
    copilot_data_dir: str = "./data"
    # SOP YAML文件目录
    copilot_sop_dir: str = "./data/sop"
    # 知识库文档目录
    copilot_knowledge_dir: str = "./data/knowledge"
    # Qdrant向量数据存储路径
    copilot_qdrant_path: str = "./data/qdrant"

    # 服务配置
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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}


settings = Settings()
