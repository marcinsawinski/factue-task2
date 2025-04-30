#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo ".env file not found. Exiting."
  exit 1
fi

# Check that required env vars are set
: "${OLLAMA_EXECUTABLE:?Need to set OLLAMA_EXECUTABLE in .env}"
: "${OLLAMA_HOST:?Need to set OLLAMA_HOST in .env}"
: "${OLLAMA_MODELS:?Need to set OLLAMA_MODELS in .env}"

# Export Ollama-specific env variables so the executable sees them
export OLLAMA_HOST
export OLLAMA_MODELS

# Set CUDA_VISIBLE_DEVICES
export CUDA_VISIBLE_DEVICES=2

# Run Ollama, passing any additional arguments
"$OLLAMA_EXECUTABLE" "$@"