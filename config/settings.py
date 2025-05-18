# config/settings.py
from pathlib import Path
from dotenv import load_dotenv
import os
import yaml

# Carga variables de .env
load_dotenv()

class Settings:
    # — PostgreSQL —
    PG_HOST: str = os.getenv("PG_HOST", "localhost")
    # Compatibilidad con PG_DB o PG_DBNAME
    PG_DATABASE: str = os.getenv("PG_DB") or os.getenv("PG_DBNAME", "")
    PG_USER: str = os.getenv("PG_USER", "")
    PG_PASSWORD: str = os.getenv("PG_PASSWORD", "")
    PG_PORT: int = int(os.getenv("PG_PORT", 5432))

    # — Excel ETL —
    EXCEL_INPUT_PATH: Path = Path(
        os.getenv("EXCEL_INPUT_PATH", "./input_excel")
    ).resolve()
    EXCEL_SHEET_NAME: str = os.getenv("EXCEL_SHEET_NAME", "Sheet1")

    # Archivo YAML adicional (opcional)
    YAML_CONFIG_FILE: Path = Path("config/excel_config.yaml").resolve()

    def __init__(self) -> None:
        # Carga configuración YAML si existe
        if self.YAML_CONFIG_FILE.exists():
            with open(self.YAML_CONFIG_FILE, "r", encoding="utf-8") as fh:
                self.yaml_cfg = yaml.safe_load(fh) or {}
        else:
            self.yaml_cfg = {}

    def get_postgres_conn_str(self) -> str:
        """
        Cadena de conexión para SQLAlchemy.
        Ejemplo: postgresql+psycopg2://user:pass@host:port/dbname
        """
        return (
            f"postgresql+psycopg2://"
            f"{self.PG_USER}:{self.PG_PASSWORD}@"
            f"{self.PG_HOST}:{self.PG_PORT}/"
            f"{self.PG_DATABASE}"
        )

    def get_excel_lookup_cfg(self) -> dict:
        """Devuelve la sub‑sección excel_lookup del YAML (o {} si no existe)."""
        return self.yaml_cfg.get("excel_lookup", {})
