import re

POSITIVE = {
    "amazing","awesome","best","better","brilliant","comfortable","easy","excellent",
    "fast","favorite","good","great","happy","helpful","impressive","love","loved",
    "perfect","reliable","smooth","strong","value","wonderful","worth","satisfied"
}
NEGATIVE = {
    "bad","broken","bug","cheap","complaint","confusing","crash","delay","difficult",
    "disappointed","disappointing","fails","fault","issue","issues","lag","late",
    "poor","problem","problems","refund","slow","terrible","unhappy","unstable",
    "useless","waste","worst"
}

def analyze_sentiment(text: str) -> dict:
    words = re.findall(r"[a-zA-Z']+", (text or "").lower())
    if not words:
        return {"label":"neutral","score":0.0,"positive_score":0.0,"negative_score":0.0,"neutral_score":1.0}

    positive = sum(1 for w in words if w in POSITIVE)
    negative = sum(1 for w in words if w in NEGATIVE)
    total = max(positive + negative, 1)
    raw = (positive - negative) / total

    if positive == negative:
        label = "neutral"
    elif raw >= 0.25:
        label = "positive"
    elif raw <= -0.25:
        label = "negative"
    else:
        label = "neutral"

    positive_score = positive / len(words)
    negative_score = negative / len(words)
    neutral_score = max(0.0, 1.0 - positive_score - negative_score)

    return {
        "label": label,
        "score": round(float(raw), 5),
        "positive_score": round(float(positive_score), 5),
        "negative_score": round(float(negative_score), 5),
        "neutral_score": round(float(neutral_score), 5),
    }
