from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ...config import settings


# ── 数据模型 ──────────────────────────────────────────

@dataclass
class SearchResult:
    chunk_text: str
    source_document: str
    heading: str
    relevance_score: float


# 存到向量表库 表里面的一条记录
@dataclass
class VectorPoint:
    # id
    id: int
    # 文本内容对应的向量
    vector: list[float]
    # 原始的文本内容
    text: str
    # 文本内容来源于知识库哪个文件 文件名
    source: str
    # 文本内容来源于知识库哪个文件哪个章节 #后面跟着的段落名
    heading: str


class VectorRepository(ABC):
    """
    向量数据库抽象
    Qdrant/Chroma/Milvus/PGVector
    不同的数据库实现这个接口然后用工厂方法暴露出去
    """

    @abstractmethod
    def init(self, collection: str, vector_size: int) -> None:
        r"""
        向量库建表 初始化collection 不存在则创建
        :param collection 表名
        :param vector_size 向量维度 每个向量是多少维
        """

    @abstractmethod
    def clear(self, collection: str) -> None:
        r"""
        清空表
        :param collection 文档数据库的表名
        """

    @abstractmethod
    def upsert(self, collection: str, points: list[VectorPoint]) -> None:
        r"""
        :param collection 向量表的表名
        :param points 要更新到向量表里面的记录
        批量写入向量
        """

    @abstractmethod
    def search(self, collection: str, query_vector: list[float], top_k: int) -> list[SearchResult]:
        r"""
        向量检索
        :param collection 表名
        :param query_vector 从向量表里面要查询的向量值
        :param top_k 指定查询条件
        :return 返回top_k结果
        """

    @abstractmethod
    def get_status(self, collection: str) -> dict:
        r"""
        查看表的状态
        :param collection 表名
        """



_repo: Optional[VectorRepository] = None


def get_repository() -> VectorRepository:
    r"""
    工厂函数
    :return: 对应的向量库 实现暴露出去
    """
    global _repo
    if _repo is None:
        impl_type = getattr(settings, "copilot_vector_type", "qdrant")
        if impl_type == "chroma":
            from .vector_repo_chroma import VectorRepositoryChroma
            _repo = VectorRepositoryChroma()
        elif impl_type == "milvus":
            from .vector_repo_milvus import VectorRepositoryMilvus
            _repo = VectorRepositoryMilvus()
        else:
            from .vector_repo_qdrant import VectorRepositoryQdrant
            _repo = VectorRepositoryQdrant()
    return _repo
