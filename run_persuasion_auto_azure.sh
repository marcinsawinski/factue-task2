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
    --prompt-name "$prompt_id" \
    --prompt-version v001 \
    --split dev \
    --max-iterations 1 \
    --seed 0 \
    --model-name GPT_4O_MINI \
    --model-provider AZURE_OPENAI \
    --model-mode CHAT \
    --part 0000 \
    --lang "*" 
done

# --resource-type OLLAMA_HOST \
# --resource-list 2 \
# --part 0000 \
# --lang pl \