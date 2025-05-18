# domain/services/transform_service.py
"""
TransformService: operaciones genéricas para limpiar o enriquecer DataFrames
y listas de dict provinientes de Business Central o Excel.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Set

try:
    from config.settings import Settings
except ImportError:  # fallback para tests
    class Settings:
        EXCLUDED_COMPANY_IDS: Set[str] = set()


class TransformService:
    """Servicio de transformaciones reutilizable en todo el proyecto."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.excluded_ids: Set[str] = getattr(Settings, "EXCLUDED_COMPANY_IDS", set())

    # ———— Company filter ————
    def filter_companies(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        if "value" not in raw:
            return {"value": []}
        filtered = [
            c for c in raw["value"] if c.get("id") not in self.excluded_ids
        ]
        return {"value": filtered}

    # ———— Drop & concat utilities ————
    def drop_columns(self, data: Dict[str, Any], cols: Set[str]) -> Dict[str, Any]:
        if "value" not in data:
            return {"value": []}
        out = [{k: v for k, v in rec.items() if k not in cols} for rec in data["value"]]
        return {"value": out}

    def concat_columns(
        self,
        data: Dict[str, Any],
        new_col: str,
        cols: List[str],
        sep: str = "_",
    ) -> Dict[str, Any]:
        if "value" not in data:
            return {"value": []}
        for rec in data["value"]:
            rec[new_col] = sep.join(str(rec.get(c, "")) for c in cols)
        return data

    def add_lookup_column(
            self,
            df: pd.DataFrame,
            lookup_dict: dict[str, Any],
            source_key_col: str,
            new_col: str,
    ) -> pd.DataFrame:
        """Añade new_col a df usando lookup_dict[source_key_col]."""
        df[new_col] = df[source_key_col].map(lookup_dict).astype("object")
        return df
