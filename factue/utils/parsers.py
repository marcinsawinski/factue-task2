import ast
import json
import re
import pandas as pd
from pandas.api.types import is_list_like
from collections import Counter, defaultdict


def safe_json_loads(s):
    # print(isinstance(s, str))

    if not isinstance(s, str):
        return {}

    # Extract the first {...} block (non-greedy to avoid nested capture)
    match = re.search(r"\{.*?\}", s, re.DOTALL)
    # print(match)
    if not match:
        return {}

    block = match.group(0)
    # print('block:', block)

    block = (
        block.replace("null", "None").replace("NA", "None").replace("false", "False").replace("true", "True")
    )

    # Try parsing the extracted block
    try:
        # print('trying json')
        return json.loads(block)
    except (json.JSONDecodeError, TypeError):
        try:
            # print('trying ast')
            return ast.literal_eval(block)
        except (ValueError, SyntaxError):
            # print('give up')
            return {}

def extract_think_and_json(text):
    result = {
        "think_content": None,
        "json_data": None,
    }

    # Extract content between <think> and </think>
    think_match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
    if think_match:
        result["think_content"] = think_match.group(1).strip()

    # Extract everything after </think>
    after_think_match = re.search(r"</think>(.*)", text, re.DOTALL)
    if after_think_match:
        after_think = after_think_match.group(1).strip()
    else:
        # If no </think>, maybe no <think> tag at all
        after_think = text.strip()

    # print("--- After </think> ---")
    # print(after_think)

    # Try to extract JSON inside ```json ... ```
    json_block_match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", after_think)
    if json_block_match:
        json_str = json_block_match.group(1)
        # print("--- Found JSON in code block ---")
        # print(json_str)
        try:
            result["json_data"] = safe_json_loads(json_str)
            return result
        except json.JSONDecodeError as e:
            pass
            # print("JSONDecodeError in code block:", e)

    # Fallback: try to extract raw JSON object
    json_fallback_match = re.search(r"(\{[\s\S]*\})", after_think)
    if json_fallback_match:
        json_str = json_fallback_match.group(1)
        # print("--- Found raw JSON ---")
        # print(json_str)
        try:
            result["json_data"] = safe_json_loads(json_str)
        except json.JSONDecodeError as e:
            pass
            # print("JSONDecodeError in fallback:", e)

    return result

def most_frequent(lst):
    if lst is None or lst is pd.NA or not hasattr(lst, "__iter__"):
        return None
    cleaned = [x for x in lst if x is not None and x is not pd.NA]
    if not cleaned:
        return None
    return Counter(cleaned).most_common(1)[0][0]


# Function to parse each row and collect all keys dynamically
def extract_all_fields_from_list_of_json_strings(list_of_json_strings):
    result = defaultdict(list)
    for s in list_of_json_strings:
        d = extract_think_and_json(s)
        result['think_content'].append(d['think_content'])
        for k in d['json_data']:
            result[k].append(d[k])
    return dict(result)
