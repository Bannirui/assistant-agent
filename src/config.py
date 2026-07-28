from pathlib import Path
from pydantic_settings import BaseSettings


# 启动后自动读取配置然后覆盖类的默认值 配置加载优先级 环境变量>.env文件>类字段默认值
class Settings(BaseSettings):
    # LLM大模型 Agent对话/推理
    # 供应商标识 deepseek/openai/qwen
    llm_provider: str = ""
    # 模型名称 deepseek-chat/gpt-4o
    llm_model: str = ""
    # API密钥
    llm_api_key: str = ""
    # API地址
    llm_base_url: str = ""

    # 向量化模型 RAG知识库检索
    # 供应商标识 dashscope/openai/local
    embed_provider: str = ""
    # 模型名称
    embed_model: str = ""
    # API密钥
    embed_api_key: str = ""
    # API地址
    embed_base_url: str = ""

    # 应用配置
    # 运行环境
    copilot_env: str = "development"
    # 日志级别
    copilot_log_level: str = "DEBUG"
    # Agent 最大工具调用轮数
    copilot_max_agent_iterations: int = 10

    # 数据路径
    copilot_data_dir: str = "./data"

    # SOP数据库 数据库类型 sqlite/mysql
    sop_db_type: str = "sqlite"

    # 知识库数据库 数据库类型 sqlite/mysql
    knowledge_db_type: str = "sqlite"

    # 知识库的文件内容存储 inline/oss 开发环境小文件可以直接存数据库 大文件存OSS
    knowledge_content_type: str = "inline"

    # SOP SQLite 文件路径
    sop_db_path: str = "./data/copilot.db"
    # 知识库 SQLite 文件路径
    knowledge_db_path: str = "./data/copilot.db"

    # SOP & 知识库 MySQL数据库连接
    db_host: str = ""
    db_port: int = 3306
    db_user: str = ""
    db_pass: str = ""
    db_name: str = "copilot"

    # 向量库类型 qdrant/chroma/milvus
    knowledge_vector_type: str = "qdrant"

    # Qdrant本地模式 向量数据存储路径
    knowledge_vector_qdrant_path: str = "./data/qdrant"

    # 服务配置
    copilot_host: str = "0.0.0.0"
    copilot_port: int = 8000

    @property
    def qdrant_path(self) -> Path:
        return Path(self.copilot_qdrant_path)

    @property
    def data_path(self) -> Path:
        return Path(self.copilot_data_dir)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}


settings = Settings()
