#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Export environment variables
export ENV=development
export DATA_PATH="$PWD/data"
export DUCKDB_FILE="$DATA_PATH/mydb.duckdb"

# Load secrets from a .env file (optional)
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

# echo "Environment loaded!"