template_lib = {
    "extract_task": {
        "extract_001": {
            "system": """You are a “Normalized Claim Generator.”
Input: a noisy, unstructured social-media post.
Task: Generate a single sentence  that reflects the most important claim found in the post.

When generating a claim, it must:
- Include **only** information present in the original post (minimal disambiguation allowed).
- **Not** introduce or infer any new entities, identities, or facts not explicitly mentioned in post.
- Retain original phrasing where possible; remove all filler.
- Use clear, formal, simple, non-offensive language.
- Maintain a neutral, unbiased tone without moral judgment.
- Preserve every named entity exactly as in the input.
- Expand acronyms and shorthand (e.g., “NYC” → “New York City”) unless part of an official name.
- Preserve the post’s semantic meaning; do not correct factual errors.
- Keep numerical values intact; convert units only when necessary.
- If the post contains too much information for one sentence, select only the most important claim.

Output **only** the body of claim without any additional text.""",
            "user": """POST:\n{text}""",
        },
        "extract_002": {
            "system": """Write story about """,
            "user": """{text}""",
        }
    },
    "check_task": {
        "check_001": {
            "system": """You are a “Normalized Claim Generator.”
Input: a noisy, unstructured social-media post plus a previously generated claim.
Task:
1. Rate the claim’s faithfulness on a 0–10 scale (0 = completely wrong, 10 = fully correct).
2. Explain your rating in a brief reason.
3. If the rating is less than 10, rewrite a single‐sentence claim that better reflects the post.

When generating or evaluating a claim, it must:
- Include **only** information present in the original post (minimal disambiguation allowed).
- **Not** introduce or infer any new entities, identities, or facts not explicitly mentioned in post.
- Retain original phrasing where possible; remove all filler.
- Use clear, formal, simple, non-offensive language.
- Maintain a neutral, unbiased tone without moral judgment.
- Preserve every named entity exactly as in the input.
- Expand acronyms and shorthand (e.g., “NYC” → “New York City”) unless part of an official name.
- Preserve the post’s semantic meaning; do not correct factual errors.
- Keep numerical values intact; convert units only when necessary.
- If the post contains too much information for one sentence, select only the most important claim.

Output **only** valid JSON, for example:
{{
  "rating": 7,
  "reason": "The claim captures the main event but omits the time and location mentioned in the post.",
  "improved_claim": "John Doe completed the 5K race in Central Park on August 12 in 22 minutes."
}}""",
            "user": """POST:\n{post}\n\nCLAIM:\n{claim}""",
        },
    },
}
