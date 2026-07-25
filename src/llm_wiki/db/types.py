"""Database types shared by models and migrations."""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Any, cast

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import UserDefinedType

JSON_VALUE: TypeEngine[Any] = JSON().with_variant(JSONB(), "postgresql")

VectorFactory = Callable[[int], TypeEngine[Any]]

try:
    _pg_vector_factory = cast(VectorFactory, import_module("pgvector.sqlalchemy").Vector)
except ImportError:  # pragma: no cover - production dependency is installed by uv
    _pg_vector_factory = None


class _FallbackVector(UserDefinedType[Any]):
    """Compile a vector column when the optional local package is absent."""

    cache_ok = True

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def get_col_spec(self, **_: Any) -> str:
        return f"VECTOR({self.dimensions})"


def vector_type(dimensions: int) -> TypeEngine[Any]:
    """Return pgvector's SQLAlchemy type with a compile-only local fallback."""

    if _pg_vector_factory is None:
        return _FallbackVector(dimensions)
    return _pg_vector_factory(dimensions)
