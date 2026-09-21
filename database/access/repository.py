"""Generic repository and entity mapping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from database.access.data_access import DataAccess

EntityT = TypeVar("EntityT")

@dataclass(frozen=True)
class EntityMapper(Generic[EntityT]):
    """
    Convert between application entities
    and database row dictionaries.
    """

    from_row: Any
    to_row: Any

    def map_from_row(self, row: Any) -> EntityT:
        """Convert a database row to an entity."""

        return self.from_row(row)

    def map_to_row(self, entity: EntityT) -> dict[str, Any]:
        """Convert an entity to a database row."""

        result = self.to_row(entity)

        if not isinstance(result, dict):
            raise TypeError("Entity mapper must return a dictionary")

        return result

class BaseRepository(Generic[EntityT]):
    """
    Generic repository providing CRUD operations.
    Concrete repositories can inherit this class
    and define table/key information.
    """

    def __init__(
        self,
        data_access: DataAccess,
        table_name: str,
        mapper: EntityMapper[EntityT],
        primary_key: str = "id",
    ) -> None:
        if not table_name.strip():
            raise ValueError("table_name must not be empty")

        if not primary_key.strip():
            raise ValueError("primary_key must not be empty")

        self.data_access = data_access
        self.table_name = table_name
        self.mapper = mapper
        self.primary_key = primary_key

    def create(self, entity: EntityT) -> EntityT:
        """Create an entity."""

        row = self.mapper.map_to_row(entity)

        if not row:
            raise ValueError("Entity row must not be empty")

        columns = list(row.keys())
        placeholders = ", ".join(["%s"] * len(columns))
        column_sql = ", ".join(f"`{column}`" for column in columns)

        sql = (
            f"INSERT INTO `{self.table_name}` "
            f"({column_sql}) "
            f"VALUES ({placeholders})"
        )
        self.data_access.execute(sql, row.values())
        return entity

    def get_by_id(self, entity_id: Any) -> EntityT | None:
        """Get an entity by primary key."""

        sql = (
            f"SELECT * FROM `{self.table_name}` "
            f"WHERE `{self.primary_key}` = %s"
        )
        row = self.data_access.query_one(sql, [entity_id])
        if row is None:
            return None
        return self.mapper.map_from_row(row)

    def list_all(self) -> list[EntityT]:
        """Return all entities."""

        sql = (f"SELECT * FROM `{self.table_name}`")
        rows = self.data_access.query(sql)
        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

    def update(self, entity_id: Any, entity: EntityT) -> EntityT:
        """Update an entity."""

        row = self.mapper.map_to_row(entity)

        if not row:
            raise ValueError("Entity row must not be empty")

        assignments = ", ".join(f"`{column}` = %s" for column in row)
        sql = (
            f"UPDATE `{self.table_name}` "
            f"SET {assignments} "
            f"WHERE `{self.primary_key}` = %s"
        )
        parameters = list(row.values())
        parameters.append(entity_id)
        self.data_access.execute(sql, parameters)

        return entity

    def delete(self, entity_id: Any) -> None:
        """Delete an entity by primary key."""

        sql = (
            f"DELETE FROM `{self.table_name}` "
            f"WHERE `{self.primary_key}` = %s"
        )
        self.data_access.execute(sql, [entity_id])