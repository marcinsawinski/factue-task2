#!/bin/bash

# Define the target directory
TARGET_DIR=".venv/lib/python3.12/site-packages/blingfire"

# Check if the target directory exists
if [ -d "$TARGET_DIR" ]; then
    echo "Target directory found: $TARGET_DIR"

    # Define the download URL for the arm64 dylib
    DYLIB_URL="https://github.com/microsoft/BlingFire/raw/master/nuget/lib/runtimes/osx-arm64/native/libblingfiretokdll.dylib"

    # Define the destination path
    DEST_PATH="$TARGET_DIR/libblingfiretokdll.dylib"


    # Download the arm64 dylib
    echo "Downloading arm64 dylib..."
    curl -L "$DYLIB_URL" -o "$DEST_PATH"

    # Verify the architecture of the downloaded dylib
    ARCH_INFO=$(file "$DEST_PATH")
    echo "Downloaded file info: $ARCH_INFO"

    if [[ "$ARCH_INFO" == *"arm64"* ]]; then
        echo "Successfully replaced with arm64 dylib."
    else
        echo "Warning: The downloaded file may not be the correct architecture."
    fi
else
    echo "Error: Target directory does not exist: $TARGET_DIR"
    exit 1
fi