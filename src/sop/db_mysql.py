r"""
MySQL占位
将来实现时需安装mysql-connector-python或aiomysql
参考SQL https://dev.mysql.com/doc/refman/8.0/en/create-table.html
"""

from .db import SopRepository, SopRecord


class SopRepositoryMySQL(SopRepository):
    def init(self) -> None:
        raise NotImplementedError("MySQL is not yet implemented")

    def load_all(self) -> list[SopRecord]:
        raise NotImplementedError("MySQL is not yet implemented")

    def upsert(self, record: SopRecord, updated_by: str = "") -> None:
        raise NotImplementedError("MySQL is not yet implemented")

    def import_from_yaml(self, yaml_dir: str = "") -> int:
        raise NotImplementedError("MySQL is not yet implemented")
