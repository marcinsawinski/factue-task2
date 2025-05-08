#!/bin/bash
clear
set -e  # Exit on error
# Manually declared list of prompt IDs
prompt_ids=(
# "Name_Calling-Labeling"
"Guilt_by_Association"
# "Doubt"
"Appeal_to_Hypocrisy"
# "Questioning_the_Reputation"
"Flag_Waving"
# "Appeal_to_Authority"
# "Appeal_to_Popularity"
# "Appeal_to_Values"
# "Appeal_to_Fear-Prejudice"
"Straw_Man"
"Red_Herring"
###################
# "Whataboutism"
# "Appeal_to_Pity"
# "Causal_Oversimplification"
# "False_Dilemma-No_Choice"
# "Consequential_Oversimplification"
# "False_Equivalence"
# "Slogans"
# "Conversation_Killer"
# "Appeal_to_Time"
# "Loaded_Language"
# "Obfuscation-Vagueness-Confusion"
# "Exaggeration-Minimisation"
# "Repetition"
)

for prompt_id in "${prompt_ids[@]}"; do
  echo "**************************************************"
  echo "Running Luigi for prompt-id: $prompt_id"
  echo "**************************************************"

  python -m factue.pipelines.persuasion_explain \
    --prompt-name "$prompt_id" \
    --prompt-version v001 \
    --resource-type aoi \
    --resource-list 0 \
    --split train \
    --max-iterations 1 \
    --seed 0 \
    --model-name GPT_41 \
    --model-provider AZURE_OPENAI \
    --model-mode CHAT \
    --part "00*" \
    --lang "*" 
done

# --resource-type OLLAMA_HOST \
# --resource-list 2 \
# --part 0000 \
# --lang pl \