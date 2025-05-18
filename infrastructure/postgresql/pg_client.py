# infrastructure/postgresql/pg_client.py
from __future__ import annotations

import logging
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


class SqlAlchemyClient:
    """
    Pequeño wrapper para crear y reutilizar un Engine de SQLAlchemy.
    Recibe la cadena DSN o la crea con get_postgres_conn_str() de Settings.
    """

    def __init__(self, dsn: str | None = None) -> None:
        from config.settings import Settings  # local import para evitar ciclos

        self.logger = logging.getLogger(__name__)
        self.dsn = dsn or Settings().get_postgres_conn_str()
        self._engine: Engine | None = None

    # ———— factory ————
    def _build_engine(self) -> Engine:
        self.logger.debug("Creando Engine Postgres…")
        return create_engine(self.dsn, pool_pre_ping=True, echo=False)

    # ———— public ————
    def get_engine(self) -> Engine:
        if self._engine is None:
            self._engine = self._build_engine()
        return self._engine

    def dispose(self) -> None:
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
