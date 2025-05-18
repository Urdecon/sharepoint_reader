Okay, aquí tienes el contenido para tu archivo `readme.md`:


# BC & Excel ETL – Clean‑Architecture Project

## Objetivo

Ingerir datos desde distintas fuentes de Business Central (API v2 & OData V4) y desde ficheros Excel hacia PostgreSQL utilizando una arquitectura de dominio limpia y pasos ETL desacoplados.

## 🗂️ Estructura principal

```markdown
project_root/
├─ application/            # Casos de uso (orquesta transform + repos)
├─ config/                 # .env loader y YAMLs (settings.py)
├─ domain/                 # Entidades + servicios puros (TransformService)
├─ infrastructure/
│   ├─ business_central/   # BCClient + BCRepository
│   ├─ filesystem/         # ExcelClient + ExcelRepository
│   └─ postgresql/         # SqlAlchemyClient + PGRepository
├─ interface_adapters/
│   └─ controllers/        # Pipelines (Extract, Transform, Store) + ETLController
├─ input/                  # Excel de entrada (fase 1)
├─ tests/                  # Pruebas unit/integration
├─ main.py                 # Pipeline completo Business Central → PG
└─ main_excel.py           # Pipeline Excel → PG
```

## ⚙️ Requisitos

| Herramienta | Versión mínima |
|-------------|----------------|
| Python      | 3.10           |
| Postgres    | 12 o superior  |

**Dependencias**

Instala todo con pip:
```bash
pip install -r requirements.txt
```
`requirements.txt` incluye: pandas, openpyxl, python-dotenv, PyYAML, sqlalchemy, psycopg2-binary, requests …

## 🔑 Variables de entorno (.env)

```ini
# PostgreSQL
PG_HOST=localhost
PG_PORT=5432
PG_DBNAME=business_central
PG_USER=postgres
PG_PASSWORD=admin

# Excel ETL
EXCEL_INPUT_PATH=./input
EXCEL_SHEET_NAME=Datos

# (Opcional) Otros secretos BC
BC_TENANT_ID=...
BC_CLIENT_ID=...
BC_CLIENT_SECRET=...
```

## Parametrización YAML

`config/excel_config.yaml` ejemplo:

```yaml
excel_lookup:
  table: companies_bc
  key_col: name
  value_col: id
  source_key_col: Empresa
  new_col: id
```

## 🚀 Ejecución rápida

```bash
# 1) ETL Business Central → PostgreSQL
python main.py

# 2) ETL Excel → PostgreSQL
python main_excel.py
```

## Qué hace cada pipeline

| Script        | Fuente                | Pasos                             | Destino           |
|---------------|-----------------------|-----------------------------------|-------------------|
| `main.py`     | BC API v2 + OData     | Extract ➜ Transform ➜ Load        | Tablas *_bc en PG |
| `main_excel.py`| Carpeta ./input (xlsx)| Concat ➜ Lookup id ➜ Añade proyecto ➜ Load | facturas_qwark    |

## ➕ Añadir nuevas tablas BC

- `BCClient` → método `fetch_*` con URL.
- `BCRepository` → wrapper `get_*`.
- `BCUseCases` → `get_company_*` (API v2) o nombre‑por‑ID (OData).
- `pipeline_extract.py` → nuevo `ExtractMultiCompanyStep`.
- `main.py` → añadir step de extracción + `StoreDataInPostgresStep`.

Para OData V4 recuerda traducir `company_id` → `company_name` con el helper interno.
```

Simplemente copia y pega este contenido en un archivo llamado `readme.md` en la raíz de tu proyecto.