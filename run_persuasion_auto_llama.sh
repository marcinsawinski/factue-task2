#!/bin/bash
clear
set -e  # Exit on error
# Manually declared list of prompt IDs
prompt_ids=(
"Name_Calling-Labeling"
"Doubt"
"Questioning_the_Reputation"
"Appeal_to_Fear-Prejudice"
"Appeal_to_Values"
"Exaggeration-Minimisation"
"Loaded_Language"
"Repetition"
)

for prompt_id in "${prompt_ids[@]}"; do
  echo "**************************************************"
  echo "Running Luigi for prompt-id: $prompt_id"
  echo "**************************************************"

  python -m factue.pipelines.persuasion_detect \
    --prompt-id "$prompt_id" \
    --prompt-version v001 \
    --split train \
    --max-iterations 5 \
    --seed -1 \
    --model-name LLAMA_31_8B \
    --model-provider OLLAMA \
    --model-mode CHAT \
    --part 0000 \
    --lang "*" \
    --resource-type OLLAMA_HOST \
    --resource-list 0123 
done

# --resource-type OLLAMA_HOST \
# --resource-list 2 \
# --part 0000 \
# --lang pl \