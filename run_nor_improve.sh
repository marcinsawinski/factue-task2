#!/bin/bash
clear
set -e  # Exit on error
python -m factue.pipelines.normalization_improve \
    --prompt-name default \
    --prompt-version v001 \
    --split dev \
    --max-iterations 10 \
    --seed 0 \
    --model-name LLAMA_31_8B \
    --model-provider OLLAMA \
    --model-mode CHAT \
    --part "0000" \
    --lang "eng" \
    "$@" 



    # --model-name DEEPSEEK_R1_8B \
    # --model-name LLAMA_31_8B \
    # --model-provider OLLAMA \
    # --resource-type OLLAMA_HOST \
    # --resource-list 0123 



    # --model-name GPT_41_MINI \
    # --model-provider AZURE_OPENAI \
    # --resource-type aoi \
    # --resource-list 01 \

    # --part 0000 \
    # --lang pl \