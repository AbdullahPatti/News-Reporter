from typing import List, Dict
import re

# Keywords that strongly indicate Pakistan relevance
PAKISTAN_KEYWORDS = [
    "pakistan", "pakistani", "islamabad", "karachi", "lahore", "peshawar",
    "rawalpindi", "quetta", "multan", "faisalabad", "hyderabad",
    "imran khan", "imran", "shehbaz", "sharif", "bhutto", "bilawal",
    "pti", "pml-n", "pmln", "ppp", "mqm", "jui", "anp",
    "balochistan", "khyber", "sindh", "punjab", "gilgit", "azad kashmir",
    "pak army", "isi", "coas", "chief justice", "supreme court",
    "rupee", "pkr", "state bank", "sbp", "fbr", "nadra",
    "cricket", "pcb", "babar azam", "shaheen", "rizwan"
]


def calculate_pakistan_score(title: str, summary: str = "", source_focus: bool = False) -> float:
    """
    Returns a score between 0.0 and 1.0
    """
    text = (title + " " + summary).lower()

    score = 0.0

    # Strong boost if source is Pakistan-focused
    if source_focus:
        score += 0.35

    # Keyword matches
    matches = 0
    for kw in PAKISTAN_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            matches += 1

    # Diminishing returns
    score += min(matches * 0.12, 0.55)

    # Extra boost for very clear Pakistan titles
    if any(k in title.lower() for k in ["pakistan", "imran", "islamabad", "karachi", "lahore"]):
        score += 0.15

    return round(min(score, 1.0), 3)


def rank_and_select(articles: List[Dict], max_pakistan: int = 10, max_world: int = 5) -> List[Dict]:
    """
    Score, sort and select top articles.
    """
    for article in articles:
        article["pakistan_score"] = calculate_pakistan_score(
            article.get("title", ""),
            article.get("summary_raw", ""),
            article.get("pakistan_focus", False)
        )
        article["is_world"] = article["pakistan_score"] < 0.45

    # Sort by score (desc) then by published date if available
    articles.sort(key=lambda x: (x["pakistan_score"], x.get("published_at") or ""), reverse=True)

    pakistan_articles = [a for a in articles if not a["is_world"]][:max_pakistan]
    world_articles = [a for a in articles if a["is_world"]][:max_world]

    return pakistan_articles + world_articles