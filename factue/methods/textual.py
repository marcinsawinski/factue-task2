from typing import Any, TypedDict

import blingfire
from fast_langdetect import detect


class LangPrediction(TypedDict):
    lang: str
    score: float


def detect_lang(text: Any) -> LangPrediction:
    if not text or not isinstance(text, str) or len(text) < 10:
        # If the text is too short or not a string, return a default value
        return LangPrediction(lang="-", score=0.0)
    text = max(text.split("\n"), key=len)
    text = blingfire.text_to_sentences(text)
    text = max(text.split("\n"), key=len)
    prediction = detect(text[:100], low_memory=False)
    lang = str(prediction.get("lang", "-"))
    score = prediction.get("score", 0.0)
    try:
        score_float = float(score)
    except (ValueError, TypeError):
        score_float = 0.0
    score_rounded = round(score_float, 2)
    return LangPrediction(lang=lang, score=score_rounded)
