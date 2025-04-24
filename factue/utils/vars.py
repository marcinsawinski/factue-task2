import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

project_root = Path(os.getenv("PROJECT_ROOT", "."))
duckdb_file_str = os.getenv("DUCKDB_FILE")

if duckdb_file_str is None:
    raise ValueError("DUCKDB_FILE environment variable is not set")
duckdb_file = project_root / duckdb_file_str
