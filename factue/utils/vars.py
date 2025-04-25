import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

project_root = Path(os.getenv("PROJECT_ROOT", "."))
duckdb_file_str = os.getenv("DUCKDB_FILE")


fasttetxt_model_path = project_root / "models" / "lid.176.bin"

if not fasttetxt_model_path.exists():
    err = f"FastText model not found at {fasttetxt_model_path}"
    raise FileNotFoundError(err)

if duckdb_file_str is None:
    raise ValueError("DUCKDB_FILE environment variable is not set")
duckdb_file = project_root / duckdb_file_str
