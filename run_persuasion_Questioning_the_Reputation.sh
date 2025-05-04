#!/bin/bash

# This script runs the lt_extract pipeline and passes any extra parameters to it
python -m factue.pipelines.persuasion_detect \
  --split train \
  --max-iterations 5 \
  --seed -1 \
  --model-name LLAMA_31_8B\
  --model-provider OLLAMA \
  --model-mode CHAT \
  --prompt-id "attack/Questioning_the_Reputation_v001"\
  --resource-type OLLAMA_HOST \
  --resource-list 012 \
  "$@" 