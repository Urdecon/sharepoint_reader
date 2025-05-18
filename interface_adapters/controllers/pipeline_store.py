# interface_adapters/controllers/pipeline_store.py
from typing import Dict, Any
import pandas as pd
import logging

from interface_adapters.controllers.etl_controller import ETLStepInterface
from infrastructure.postgresql.pg_repository import PGRepository


class CheckPostgresConnectionStep(ETLStepInterface):
    def __init__(self, repo: PGRepository) -> None:
        self.repo = repo
        self.logger = logging.getLogger(__name__)

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.repo.check_connection():
            raise RuntimeError("Postgres no disponible")
        return context


class StoreDataInPostgresStep(ETLStepInterface):
    def __init__(
        self,
        pg_repository: PGRepository,
        context_key: str,
        table_name: str,
        primary_key: str | None = None,
        convert_json_to_df: bool = False,
    ) -> None:
        self.repo = pg_repository
        self.context_key = context_key
        self.table_name = table_name
        self.primary_key = primary_key
        self.convert_json_to_df = convert_json_to_df
        self.logger = logging.getLogger(__name__)

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        data = context.get(self.context_key)
        if data is None:
            self.logger.warning("Contexto sin clave %s", self.context_key)
            return context

        # Normaliza a DataFrame
        if isinstance(data, pd.DataFrame):
            df = data
        elif self.convert_json_to_df and isinstance(data, dict):
            df = pd.DataFrame(data.get("value", []))
        else:
            raise RuntimeError(f"Tipo de datos inesperado para {self.context_key}")

        if self.primary_key:
            self.repo.incremental_insert_table(self.table_name, df, self.primary_key)
        else:
            self.repo.insert_table(self.table_name, df, if_exists="append")

        return context
