# infrastructure/postgresql/pg_repository.py
from __future__ import annotations

import logging
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from infrastructure.postgresql.pg_client import SqlAlchemyClient


class PGRepository:
    """Operaciones de alto nivel contra Postgres (check, insert incremental, etc.)."""

    def __init__(self, sa_client: SqlAlchemyClient) -> None:
        self.sa_client = sa_client
        self.logger = logging.getLogger(__name__)

    # ———— Health check ————
    def check_connection(self) -> bool:
        try:
            with self.sa_client.get_engine().connect() as conn:
                conn.execute(text("SELECT 1"))
            self.logger.info("Conexión a Postgres OK.")
            return True
        except SQLAlchemyError as exc:
            self.logger.error("Postgres KO: %s", exc)
            return False

    # ———— Inserción simple ————
    def insert_table(
        self,
        table_name: str,
        df: pd.DataFrame,
        if_exists: str = "append",
        primary_key: str | None = None,
    ) -> None:
        engine = self.sa_client.get_engine()
        df.to_sql(table_name, engine, if_exists=if_exists, index=False, method="multi")
        if primary_key and if_exists == "replace":
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE "{table_name}" ADD PRIMARY KEY ("{primary_key}")'))

    # ———— Inserción incremental por PK ————
    def incremental_insert_table(
        self,
        table_name: str,
        df_new: pd.DataFrame,
        primary_key: str,
    ) -> None:
        engine = self.sa_client.get_engine()

        if df_new.empty:
            self.logger.info("DF vacío, nada que insertar.")
            return

        with engine.begin() as conn:
            existing = pd.read_sql(text(f'SELECT "{primary_key}" FROM "{table_name}"'), conn)
            to_insert = df_new[~df_new[primary_key].isin(existing[primary_key])]
            if not to_insert.empty:
                to_insert.to_sql(table_name, conn, if_exists="append", index=False, method="multi")
                self.logger.info("Insertadas %d filas nuevas en %s.", len(to_insert), table_name)
            else:
                self.logger.info("No hay filas nuevas para %s.", table_name)

    def fetch_lookup_dict(
            self,
            table: str,
            key_col: str,
            value_col: str,
    ) -> dict[str, Any]:
        q = f'SELECT "{key_col}", "{value_col}" FROM "{table}"'
        engine = self.sa_client.get_engine()
        df = pd.read_sql(q, engine)
        return dict(zip(df[key_col], df[value_col]))
