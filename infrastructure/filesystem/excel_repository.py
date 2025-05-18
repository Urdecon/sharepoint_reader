import logging
from typing import Dict, Any
import pandas as pd

from infrastructure.filesystem.excel_client import ExcelClient


class ExcelRepository:
    """
    Encapsula la obtención y validación del DataFrame leído por ExcelClient.
    """

    def __init__(self, client: ExcelClient) -> None:
        self.client = client
        self.logger = logging.getLogger(__name__)

    def get_combined_dataframe(self) -> Dict[str, Any]:
        df: pd.DataFrame = self.client.fetch_all_excels()
        self.logger.info("ExcelRepository: %d filas leídas", len(df))
        return {"value": df}
