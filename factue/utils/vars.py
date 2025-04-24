import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
project_root = Path(os.getenv("PROJECT_ROOT"))
duckdb_file = project_root / os.getenv("DUCKDB_FILE")
