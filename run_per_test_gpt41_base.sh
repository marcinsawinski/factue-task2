#!/bin/bash
clear
set -e  # Exit on error
# Manually declared list of prompt IDs
prompt_ids=(
"Appeal_to_Hypocrisy"
"Appeal_to_Values"
"Appeal_to_Authority"
"Appeal_to_Pity"
"Appeal_to_Popularity"
"Conversation_Killer"
"Guilt_by_Association"
"Appeal_to_Fear-Prejudice"
"Whataboutism"
"Repetition"
"Loaded_Language"
"Appeal_to_Time"
"Slogans"
"Doubt"
"Flag_Waving"
"Name_Calling-Labeling"
"Questioning_the_Reputation"
"Exaggeration-Minimisation"
"Causal_Oversimplification"
"False_Dilemma-No_Choice"
"False_Equivalence"
"Obfuscation-Vagueness-Confusion"
"Red_Herring"
"Consequential_Oversimplification"
"Straw_Man"
)

for prompt_id in "${prompt_ids[@]}"; do
  echo "**************************************************"
  echo "Running Luigi for prompt-id: $prompt_id"
  echo "**************************************************"

  python -m factue.pipelines.persuasion_detect \
    --prompt-name "$prompt_id" \
    --prompt-version v002 \
    --split dev \
    --max-iterations 1 \
    --seed 0 \
    --model-name GPT_41_MINI \
    --model-provider AZURE_OPENAI \
    --model-mode CHAT \
    --part "000*" \
    --lang "pl" 
done
    # --resource-type aoi \
    # --resource-list 0 \
# --resource-type OLLAMA_HOST \
# --resource-list 2 \
# --part 0000 \
# --lang pl \