import ast
import json
import re
from collections import Counter, defaultdict

import demjson3
import pandas as pd
from jsonschema import ValidationError, validate


def replace_empty_dicts_in_list(x):
    if isinstance(x, list):
        return [None if isinstance(i, dict) and not i else i for i in x]
    return x


def extract_json_from_payload(payload):
    # Extract <think> content
    think_match = re.search(
        r"<think>(.*?)</think>", payload, flags=re.DOTALL | re.IGNORECASE
    )
    think_content = think_match.group(1).strip() if think_match else None

    # Remove <think>...</think> block
    payload_wo_think = re.sub(
        r"<think>.*?</think>", "", payload, flags=re.DOTALL | re.IGNORECASE
    )

    # Remove Markdown code fences and XML-like tags
    cleaned = re.sub(
        r"```json|```|<[^>]+>", "", payload_wo_think, flags=re.IGNORECASE
    ).strip()

    # Find the first valid JSON object
    json_match = re.search(r"{.*?}", cleaned, flags=re.DOTALL)
    json_str = json_match.group(0).strip() if json_match else None

    # Extract any extra content apart from think and json
    extra_content = (
        cleaned.replace(json_str, "", 1).strip() if json_str else cleaned.strip()
    )
    extra_content = extra_content if extra_content else None

    return json_str, think_content, extra_content


def normalize_keys(data):
    return {k.lower(): v for k, v in data.items()}


def coerce_boolean_fields(data, boolean_fields):
    illegal_values = {}
    for field in boolean_fields:
        if field in data:
            original_value = data[field]
            if isinstance(original_value, str):
                val = original_value.strip().lower()
                if val in ["true", "yes", "1"]:
                    data[field] = True
                elif val in ["null", "none", "na", "false", "no", "0"]:
                    data[field] = False
                else:
                    data[field] = False
                    illegal_values[field] = original_value
            elif isinstance(original_value, (int, float)):
                data[field] = bool(original_value)
            elif isinstance(original_value, bool):
                pass
            else:
                data[field] = False
                illegal_values[field] = original_value
    if not illegal_values:
        illegal_values = None
    return illegal_values


def coerce_null_values(data):
    for k, v in data.items():
        if isinstance(v, str) and v.strip().lower() in ["null", "none", "na"]:
            data[k] = None
    return data


def validate_response(payload, schema, error=None):

    result = {"raw": payload}

    if error is not None:
        result["error"] = error

    if schema is None:
        result.update({"is_valid": True, "status": "no validation"})
        return result

    schema_properties = {k.lower(): v for k, v in schema["properties"].items()}
    required_fields = [k.lower() for k in schema["required"]]
    boolean_fields = [
        k for k, v in schema_properties.items() if v.get("type") == "boolean"
    ]

    result.update({key: None for key in schema_properties})

    if payload is None:
        return result

    raw_json, think_content, extra_content = extract_json_from_payload(payload)
    # print('extract_json_from_payload:',raw_json, think_content, extra_content, sep='\n')

    result.update(
        {
            "extra_properties": None,
            "think_content": think_content,
            "extra_content": extra_content,
            "illegal_value": {},
            "is_valid": False,
        }
    )

    if not raw_json:
        return result

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        try:
            data = ast.literal_eval(raw_json)
        except Exception:
            try:
                data = demjson3.decode(raw_json)
            except Exception:
                return result

    data = normalize_keys(data)
    data = coerce_null_values(data)
    illegal_values = coerce_boolean_fields(data, boolean_fields)

    lower_schema = {
        "type": schema["type"],
        "properties": schema_properties,
        "required": required_fields,
        "additionalProperties": schema.get("additionalProperties", True),
    }

    try:
        validate(instance=data, schema=lower_schema)
    except ValidationError:
        return result

    allowed_keys = set(schema_properties.keys())
    actual_keys = set(data.keys())
    extra_keys = actual_keys - allowed_keys

    extra_properties = (
        {key: data.pop(key) for key in extra_keys} if extra_keys else None
    )
    if extra_properties:
        result["extra_properties"] = json.dumps(extra_properties)

    for key in schema_properties:
        result[key] = data.get(key)

    result["illegal_value"] = (
        illegal_values  # {k: illegal_values.get(k, "ok") for k in boolean_fields}
    )
    result["is_valid"] = all(field in data for field in required_fields)
    return result


def expand_series_of_dict_lists(series):
    # Extract all keys from all dicts to get full set of keys
    all_keys = set()
    for lst in series:  # .dropna():
        for d in lst:
            all_keys.update(d.keys())

    # For each row, create a dict: key -> list of values for that key
    def extract_keys(dicts):
        return {key: [d.get(key) for d in dicts] for key in all_keys}

    return series.apply(extract_keys).apply(pd.Series)


##################################################### old ################################################
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
        block.replace("null", "None")
        .replace("NA", "None")
        .replace("false", "False")
        .replace("true", "True")
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
    result = {"think_content": None, "json_data": {}, "orignal": text}

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


def normalize_binary(data):
    result = -1
    if str(data).strip().lower() in {"1", "true"}:
        result = 1
    if str(data).strip().lower() in {"0", "false"}:
        result = 0
    return result


def normalize_binary_list(data):
    if isinstance(data, list):
        return [normalize_binary(x) for x in data]
    else:
        return normalize_binary(data)


# Function to parse each row and collect all keys dynamically
def extract_all_fields_from_list_of_json_strings(list_of_json_strings):
    result = defaultdict(list)
    for s in list_of_json_strings:
        d = extract_think_and_json(s)
        if d is not None and d:
            result["think_content"].append(d["think_content"])
            for k in d.get(
                "json_data", {"error": "could not extract json from output"}
            ):
                result[k].append(d["json_data"][k])
        else:
            result["error"].append("No content extracted")
    return dict(result)
