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
        d = safe_json_loads(s)
        for k in d:
            result[k].append(d[k])
    return dict(result)
