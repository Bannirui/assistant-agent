r"""
OSS 存储后端。
MinIO:   开源，S3兼容，可自建  https://min.io/docs/
阿里 OSS: 阿里云对象存储  https://help.aliyun.com/product/31815.html
"""

from .content_store import ContentStore


class ContentStoreOSS(ContentStore):
    """大文件存 OSS 数据库只存 URL"""

    def get(self, doc_id: int) -> str | None:
        raise NotImplementedError("OSS backend is not yet implemented")

    def put(self, doc_id: int, content: str) -> str | None:
        raise NotImplementedError("OSS backend is not yet implemented")

    def delete(self, doc_id: int) -> None:
        raise NotImplementedError("OSS backend is not yet implemented")


# ── 具体实现占位 ──

class ContentStoreMinio(ContentStoreOSS):
    """MinIO 实现 (S3 API 兼容)"""
    def get(self, doc_id: int) -> str | None:
        raise NotImplementedError("MinIO is not yet implemented")

    def put(self, doc_id: int, content: str) -> str | None:
        raise NotImplementedError("MinIO is not yet implemented")

    def delete(self, doc_id: int) -> None:
        raise NotImplementedError("MinIO is not yet implemented")


class ContentStoreAliOSS(ContentStoreOSS):
    """阿里云 OSS 实现"""
    def get(self, doc_id: int) -> str | None:
        raise NotImplementedError("AliOSS is not yet implemented")

    def put(self, doc_id: int, content: str) -> str | None:
        raise NotImplementedError("AliOSS is not yet implemented")

    def delete(self, doc_id: int) -> None:
        raise NotImplementedError("AliOSS is not yet implemented")
