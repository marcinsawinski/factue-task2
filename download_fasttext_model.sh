#!/bin/bash

# Define the target directory
MODEL_DIR="factue/models"
MODEL_URL="https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
MODEL_FILE="$MODEL_DIR/lid.176.bin"

# Create the directory if it doesn't exist
mkdir -p "$MODEL_DIR"

# Download the model if it doesn't already exist
if [ ! -f "$MODEL_FILE" ]; then
    echo "Downloading FastText language identification model..."
    curl -L "$MODEL_URL" -o "$MODEL_FILE"
    echo "Download complete: $MODEL_FILE"
else
    echo "Model already exists at $MODEL_FILE"
fi