#!/bin/bash
clear
set -e  # Exit on error
python -m factue.pipelines.normalization_cleanup \
    --prompt-name default \
    --prompt-version v001 \
    --split train \
    --max-iterations 1 \
    --seed 0 \
    --model-name GPT_41_MINI \
    --model-provider AZURE_OPENAI \
    --model-mode CHAT \
    --part "*" \
    --lang "*" \
    "$@" 

# --resource-type aoi \
# --resource-list 01 \
# --part 0000 \
# --lang pl \
    # --part "Appeal_to_Popularity" \