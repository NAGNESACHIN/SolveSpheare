import re
from .sentiment import analyze_sentiment

ASPECT_KEYWORDS = {
    "battery": ["battery", "battery life", "charging", "charge"],
    "performance": ["performance", "speed", "fast", "slow", "lag", "processor"],
    "camera": ["camera", "photo", "photos", "video", "picture", "pictures"],
    "display": ["display", "screen", "brightness", "resolution", "touch"],
    "design": ["design", "build", "look", "looks", "material", "weight"],
    "price": ["price", "cost", "expensive", "cheap", "value", "money"],
    "software": ["software", "app", "apps", "update", "updates", "ui", "interface"],
    "delivery": ["delivery", "shipping", "shipment", "arrived", "package"],
    "customer service": ["support", "service", "customer service", "seller", "refund"],
    "quality": ["quality", "durable", "durability", "broken", "defect"],
}

def extract_aspects(text: str) -> list[dict]:
    source = text or ""
    lowered = source.lower()
    results = []
    seen = set()

    for aspect, keywords in ASPECT_KEYWORDS.items():
        for keyword in keywords:
            start = 0
            while True:
                pos = lowered.find(keyword, start)
                if pos < 0:
                    break
                end = pos + len(keyword)
                key = (aspect, pos, end)
                if key not in seen:
                    left = max(0, pos - 80)
                    right = min(len(source), end + 80)
                    context = source[left:right]
                    sentiment = analyze_sentiment(context)
                    results.append({
                        "aspect": aspect,
                        "mention_text": source[pos:end],
                        "sentiment": sentiment,
                        "start_position": pos,
                        "end_position": end,
                        "confidence": 0.85 if keyword == aspect else 0.72,
                    })
                    seen.add(key)
                start = end

    return results
