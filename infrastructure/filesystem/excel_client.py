from pathlib import Path
from typing import List, Dict, Any
import logging

import pandas as pd
from config.settings import Settings


class ExcelClient:
    """
    Lee uno o varios archivos Excel del disco (fase 1).
    En el futuro la clase podrá heredar de esta y sobreescribir
    `list_excels()` y `load_excel()` para SharePoint.
    """

    def __init__(self, settings: Settings) -> None:
        self.base_path: Path = settings.EXCEL_INPUT_PATH
        self.sheet_name: str = settings.EXCEL_SHEET_NAME
        self.logger = logging.getLogger(__name__)

    # ------- helpers -----------------------------------------------------
    def list_excels(self) -> List[Path]:
        return list(self.base_path.glob("*.xlsx"))

    def load_excel(self, file: Path) -> pd.DataFrame:
        self.logger.debug("Leyendo %s", file.name)
        return pd.read_excel(file, sheet_name=self.sheet_name)

    # ------- interfaz pública -------------------------------------------
    def fetch_all_excels(self) -> pd.DataFrame:
        frames: List[pd.DataFrame] = []
        for fp in self.list_excels():
            frames.append(self.load_excel(fp))
        if frames:
            return pd.concat(frames, ignore_index=True)
        return pd.DataFrame()  # vacío
