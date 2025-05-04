#!/bin/bash
# --resource-type OLLAMA_HOST \
# --resource-list 2 \
# --prompt-id "attack/Questioning_the_Reputation_v001"\

clear
set -e  # Exit on error
BASE_PATH="prompts/persuasion/detect"

# Find all YAML files under the base path
find "$BASE_PATH" -type f -name "*.yaml" | while read -r file; do
    # Get the prompt ID (relative path to base)
    relative_path="${file#$BASE_PATH/}"
    prompt_id="${relative_path%.yaml}"

    echo "**************************************************"
    echo "Running Luigi for prompt-id: $prompt_id"
    echo "**************************************************"
    python -m factue.pipelines.persuasion_detect \
    --prompt-id "$prompt_id" \
    --split trial \
    --max-iterations 1 \
    --seed 0 \
    --model-name GPT_4O_MINI \
    --model-provider AZURE_OPENAI \
    --model-mode CHAT \
    --part 0000 \
    --lang pl 
done