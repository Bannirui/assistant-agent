r"""
本地向量模型 不依赖外部API 直接在CPU上跑

模型选择
  BAAI/bge-small-zh-v1.5            24MB    快速         中文够用
  BAAI/bge-large-zh-v1.5           326MB   效果最好      需要更多内存
  shibing624/text2vec-base-chinese 400MB   另一款中文模型
"""

from typing import Optional

from ..provider import LLMProvider


class LocalEmbeddingProvider(LLMProvider):
    """本地CPU运行向量模型 零API依赖"""

    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        self.model_name = model_name
        self._model: Optional[object] = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def chat(self, messages: list, tools: Optional[list] = None):
        raise NotImplementedError("本地模型只做向量化 不支持聊天")

    def embed(self, texts: list[str]) -> list[list[float]]:
        model = self._get_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
