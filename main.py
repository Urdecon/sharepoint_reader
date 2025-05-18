# main_excel.py
# ------------------------------------------------------------------------------
# ETL que:
#   1) Lee todos los .xlsx de la carpeta EXCEL_INPUT_PATH (hoja EXCEL_SHEET_NAME)
#   2) Concatena en un único DataFrame
#   3) Enlaza CompanyId usando la tabla companies_bc (name → id)
#   4) Inserta / actualiza en Postgres (tabla excel_data_bc)
# ------------------------------------------------------------------------------

import logging
import sys
from pathlib import Path
import pandas as pd

# ─── Imports de la app ────────────────────────────────────────────────────────
from config.settings import Settings

from infrastructure.filesystem.excel_client import ExcelClient
from infrastructure.filesystem.excel_repository import ExcelRepository

from infrastructure.postgresql.pg_client import SqlAlchemyClient
from infrastructure.postgresql.pg_repository import PGRepository

from domain.services.transform_service import TransformService
from application.use_cases.excel_use_cases import ExcelUseCases

from interface_adapters.controllers.pipeline_excel_extract import ExtractExcelStep
from interface_adapters.controllers.pipeline_store import (
    StoreDataInPostgresStep,
    CheckPostgresConnectionStep,
)
from interface_adapters.controllers.etl_controller import ETLController

# ─── Logging global ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main() -> None:
    logger.info("========== ETL Excel → Postgres ==========")

    # 1. Dependencias
    settings = Settings()
    excel_client = ExcelClient(settings)
    excel_repo = ExcelRepository(excel_client)

    pg_repo = PGRepository(SqlAlchemyClient())
    ts = TransformService()

    excel_uc = ExcelUseCases(excel_repo, pg_repo, ts)

    # 2. Steps
    step_extract_excel = ExtractExcelStep(excel_uc, out_context_key="excel_df")

    step_check_pg = CheckPostgresConnectionStep(pg_repo)

    step_store_excel = StoreDataInPostgresStep(
        pg_repository=pg_repo,
        context_key="excel_df",
        table_name="facturas_qwark",
        convert_json_to_df=False,   # ya es DataFrame
        primary_key=None,          # crea sin PK o añade después
    )

    steps = [
        step_extract_excel,
        step_check_pg,
        step_store_excel,
    ]
    logger.info("Pipeline construido con %d steps.", len(steps))

    # 3. Run
    try:
        ETLController(steps).run_etl_process()
        logger.info("✅ ETL Excel finalizado con éxito.")
    except Exception as exc:
        logger.exception("❌ Fallo en ETL Excel:")
        sys.exit(1)


if __name__ == "__main__":
    main()
