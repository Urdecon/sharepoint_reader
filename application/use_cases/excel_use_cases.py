# application/use_cases/excel_use_cases.py
"""
Casos de uso para el ETL‑Excel.

1. Lee y concatena todos los .xlsx de la carpeta EXCEL_INPUT_PATH.
2. Enlaza cada registro con companies_bc mediante Empresa → id.
3. Genera la columna «proyecto»:
     • Toma los 4 primeros caracteres de «Unidad de negocio».
     • Si esos 4 son dígitos ⇒ «PY_00<4‑dígitos>» (ej. 2427 → PY_002427).
     • Si no son dígitos ⇒ copia el texto original.
4. Devuelve el DataFrame para almacenar en Postgres.
"""

from __future__ import annotations

import logging
from typing import Dict, Any

import pandas as pd

from domain.services.transform_service import TransformService
from config.settings import Settings
from infrastructure.postgresql.pg_repository import PGRepository
from infrastructure.filesystem.excel_repository import ExcelRepository


class ExcelUseCases:
    """Orquesta la lectura y transformaciones del DataFrame concatenado."""

    def __init__(
        self,
        excel_repo: ExcelRepository,
        pg_repo: PGRepository,
        transform_service: TransformService,
    ) -> None:
        self.repo = excel_repo
        self.pg_repo = pg_repo
        self.ts = transform_service
        self.settings = Settings()
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------ #
    def _enrich_with_company_id(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade la columna id con lookup contra companies_bc."""
        cfg = self.settings.get_excel_lookup_cfg()
        if not cfg:
            return df

        lookup = self.pg_repo.fetch_lookup_dict(
            table=cfg["table"],
            key_col=cfg["key_col"],
            value_col=cfg["value_col"],
        )
        df = self.ts.add_lookup_column(
            df,
            lookup,
            source_key_col=cfg["source_key_col"],
            new_col=cfg["new_col"],
        )
        return df

    def _add_proyecto_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea 'proyecto':
        - 4 primeros caracteres de «Unidad de negocio».
        - Si son dígitos -> PY_00<4dígitos>, si no, copia texto original.
        """
        src_col = "Unidad de negocio"
        if src_col not in df.columns:
            self.logger.warning("Columna '%s' no encontrada en DataFrame.", src_col)
            return df

        def _build(val: str) -> str:
            head = (val or "")[:4]
            return f"PY_00{head}" if head.isdigit() else val

        df["proyecto"] = df[src_col].astype(str).apply(_build)
        return df

    # ------------------------------------------------------------------ #
    def get_excel_dataframe(self) -> Dict[str, Any]:
        """Devuelve DataFrame final listo para cargar en Postgres."""
        df: pd.DataFrame = self.repo.get_combined_dataframe()["value"]

        if df.empty:
            self.logger.warning("DataFrame concatenado está vacío.")
            return {"value": df}

        df = self._enrich_with_company_id(df)
        df = self._add_proyecto_column(df)
        return {"value": df}
