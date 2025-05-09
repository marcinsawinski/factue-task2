#!/bin/bash
clear
set -e  # Exit on error
# Manually declared list of prompt IDs
prompt_ids=(
"incremental_base"
)

for prompt_id in "${prompt_ids[@]}"; do
  echo "**************************************************"
  echo "Running Luigi for prompt-id: $prompt_id"
  echo "**************************************************"

  python -m factue.pipelines.persuasion_define \
    --prompt-name "$prompt_id" \
    --prompt-version v001 \
    --resource-type aoi \
    --resource-list 01 \
    --split train \
    --max-iterations 1 \
    --seed 0 \
    --model-name GPT_41_MINI \
    --model-provider AZURE_OPENAI \
    --model-mode CHAT \
    --part "*" \
    --lang "*" \
    "$@" 
done

# --resource-type aoi \
# --resource-list 01 \
# --part 0000 \
# --lang pl \
    # --part "Appeal_to_Popularity" \