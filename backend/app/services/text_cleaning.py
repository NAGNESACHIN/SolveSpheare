import re

def clean_text(text: str) -> str:
    text = (text or "").replace("\\r", " ").replace("\\n", " ").replace("\\t", " ")
    text = re.sub(r"https?://\\S+|www\\.\\S+", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^\\w\\s.,!?'-]", " ", text, flags=re.UNICODE)
    return re.sub(r"\\s+", " ", text).strip()
