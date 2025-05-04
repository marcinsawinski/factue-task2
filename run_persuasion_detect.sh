#!/bin/bash

# This script runs the lt_extract pipeline and passes any extra parameters to it

python -m factue.pipelines.persuasion_detect \
  --split train \
  --max-iterations 1 \
  --seed -1 \
  --model-name LLAMA_31_8B\
  --model-provider OLLAMA \
  --model-mode CHAT \
  --prompt-id "justification/Appeal_to_Values_v001"\
  --part 0000 \
  --lang pl \
  "$@" 