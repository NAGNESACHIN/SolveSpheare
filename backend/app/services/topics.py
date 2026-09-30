from collections import Counter
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

def discover_topics(texts: list[str], max_topics: int = 5) -> list[dict]:
    cleaned = [t.strip() for t in texts if t and t.strip()]
    if len(cleaned) < 3:
        return []

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        max_features=1000,
    )
    matrix = vectorizer.fit_transform(cleaned)
    if matrix.shape[1] == 0:
        return []

    n_topics = min(max_topics, matrix.shape[0], matrix.shape[1])
    if n_topics < 1:
        return []

    model = NMF(n_components=n_topics, init="nndsvda", random_state=42, max_iter=400)
    weights = model.fit_transform(matrix)
    terms = vectorizer.get_feature_names_out()
    topics = []

    for topic_index, component in enumerate(model.components_):
        top_indices = component.argsort()[::-1][:8]
        keywords = [str(terms[i]) for i in top_indices if component[i] > 0]
        name = " / ".join(keywords[:3]) or f"Topic {topic_index + 1}"
        topics.append({
            "index": topic_index,
            "name": name[:255],
            "keywords": keywords,
            "weights": weights[:, topic_index],
        })

    return topics
