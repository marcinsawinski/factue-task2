#!/bin/bash
ifneq (,$(wildcard .env))
	include .env
	export
endif

# Default path if PYTHON_ENV_PATH is not set
PYTHON_ENV_PATH ?= .venv
# Activate virtual environment
source $(PYTHON_ENV_PATH)/bin/activate

# Export environment variables
export DATA_PATH="$PWD/data"
export DUCKDB_FILE="$DATA_PATH/mydb.duckdb"

# Load secrets from a .env file (optional)
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

# echo "Environment loaded!"