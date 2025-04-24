#!/bin/bash

# Activate virtual environment
source .venv/bin/activate
dvc remote add -d gdrive_remote gdrive://1zprn64WNQ2lPphARYMgRIUOp-u0XEQ2n
dvc remote modify gdrive_remote gdrive_use_service_account true
dvc remote modify gdrive_remote gdrive_service_account_json_file_path gdrive-creds.json