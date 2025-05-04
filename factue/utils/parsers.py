import ast
import json
import re
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
        block.replace("null", "None").replace("false", "False").replace("true", "True")
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
    if not lst:
        return None
    return Counter(lst).most_common(1)[0][0]


# Function to parse each row and collect all keys dynamically
def extract_all_fields_from_list_of_json_strings(list_of_json_strings):
    result = defaultdict(list)
    for s in list_of_json_strings:
        d = safe_json_loads(s)
        for k in d:
            result[k].append(d[k])
    return dict(result)
