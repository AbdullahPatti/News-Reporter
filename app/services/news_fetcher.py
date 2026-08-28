import feedparser
import httpx
from datetime import datetime, timezone
from typing import List, Dict, Optional
from urllib.parse import urlparse
import time

# Recommended free sources
DEFAULT_SOURCES = [
    {
        "name": "Dawn",
        "source_type": "rss",
        "url": "https://www.dawn.com/feeds/home",
        "pakistan_focus": True,
        "weight": 1.4
    },
    {
        "name": "The News",
        "source_type": "rss",
        "url": "https://www.thenews.com.pk/rss/1/1",
        "pakistan_focus": True,
        "weight": 1.2
    },
    {
        "name": "Express Tribune",
        "source_type": "rss",
        "url": "https://tribune.com.pk/feed/home",
        "pakistan_focus": True,
        "weight": 1.2
    },
    {
        "name": "BBC News",
        "source_type": "rss",
        "url": "https://feeds.bbci.co.uk/news/rss.xml",
        "pakistan_focus": False,
        "weight": 1.0
    },
    {
        "name": "Al Jazeera",
        "source_type": "rss",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "pakistan_focus": False,
        "weight": 1.0
    },
    {
        "name": "Reuters World",
        "source_type": "rss",
        "url": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
        "pakistan_focus": False,
        "weight": 1.1
    },
]


def fetch_rss(url: str) -> List[Dict]:
    """Fetch and parse an RSS feed. Returns list of normalized articles."""
    try:
        feed = feedparser.parse(url)
        articles = []

        for entry in feed.entries[:15]:  # limit per source
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

            articles.append({
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", "").strip(),
                "summary_raw": entry.get("summary", entry.get("description", "")).strip()[:1000],
                "published_at": published,
                "content": entry.get("summary", entry.get("description", "")).strip()[:3000],
            })

        return articles
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []


def fetch_all_sources(sources: List[Dict] = None) -> List[Dict]:
    """
    Fetch from all sources and return a flat list of articles
    with source metadata attached.
    """
    if sources is None:
        sources = DEFAULT_SOURCES

    all_articles = []

    for source in sources:
        print(f"Fetching: {source['name']}...")
        items = fetch_rss(source["url"])

        for item in items:
            if not item["title"] or not item["url"]:
                continue

            item["source_name"] = source["name"]
            item["source_type"] = source["source_type"]
            item["pakistan_focus"] = source["pakistan_focus"]
            item["weight"] = source["weight"]
            all_articles.append(item)

        time.sleep(0.8)

    return all_articles