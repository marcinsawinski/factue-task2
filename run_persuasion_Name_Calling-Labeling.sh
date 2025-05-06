#!/bin/bash
clear
  # --part 0000 \
  # --lang pl \
  # --resource-type OLLAMA_HOST \
  # --resource-list 0 \

# This script runs the lt_extract pipeline and passes any extra parameters to it
python -m factue.pipelines.persuasion_detect \
  --split train \
  --max-iterations 5 \
  --seed -1 \
  --model-name LLAMA_32_3B\
  --model-provider OLLAMA \
  --model-mode CHAT \
  --prompt-name "Name_Calling-Labeling"\
  --prompt-version "v001"\
  --resource-type OLLAMA_HOST \
  --resource-list 23 
  "$@" 