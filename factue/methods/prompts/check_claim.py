templates_check_claim = {
    "v001": """
You are an expert journalist and fact-checker. Your task is to compare an extracted claim with the original post and determine whether the claim accurately reflects the source content.
For each of the following questions, answer `true` or `false` based on your analysis. If your answer is `false`, provide a list of specific errors. If `true`, keep the list empty.
Strictly respond in the following JSON format:

{{
  "questions": [
    {{
      "id": "meaning_preserved",
      "answer": true | false,
      "errors": [ "..." ]
    }},
    {{
      "id": "correct_named_entities",
      "answer": true | false,
      "errors": [ "..." ]
    }},
    {{
      "id": "correct_numbers",
      "answer": true | false,
      "errors": [ "..." ]
    }},
    {{
      "id": "no_added_data",
      "answer": true | false,
      "errors": [ "..." ]
    }},
    {{
      "id": "no_missing_data",
      "answer": true | false,
      "errors": [ "..." ]
    }}
  ]
}}

CLAIM:
\"\"\"{claim}\"\"\"

POST:
\"\"\"{post}\"\"\"
""",
    "v002": """
You are an expert journalist and fact-checker. Your task is to compare an extracted claim with the original post and determine whether the claim accurately reflects the source content.

CLAIM:
\"\"\"{claim}\"\"\"

POST:
\"\"\"{post}\"\"\"
""",
    "v003": """
Does the claim accurately reflect the source content in the post?

CLAIM:
\"\"\"{claim}\"\"\"

POST:
\"\"\"{post}\"\"\"
""",
}
