import blingfire
from fast_langdetect import detect


def detect_lang(text):
    if not text or not isinstance(text, str) or len(text) < 10:
        # If the text is too short or not a string, return a default value
        return {"lang": "-", "score": 0.0}
    text = max(text.split("\n"), key=len)
    text = blingfire.text_to_sentences(text)
    text = max(text.split("\n"), key=len)
    prediction = detect(text[:100], low_memory=False)
    prediction.update({"score": round(prediction["score"], 2)})
    return prediction
