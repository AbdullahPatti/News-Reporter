from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Dict

from app.models import Source, RawArticle
from app.services.ranker import rank_and_select


def get_or_create_source(db: Session, name: str, source_type: str, url: str, 
                         pakistan_focus: bool, weight: float) -> Source:
    source = db.query(Source).filter(Source.name == name).first()
    if source:
        return source

    source = Source(
        name=name,
        source_type=source_type,
        url=url,
        pakistan_focus=pakistan_focus,
        weight=weight,
        is_active=True
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def save_articles(db: Session, raw_articles: List[Dict]) -> int:
    """
    Rank articles and save new ones into raw_articles table.
    Returns number of newly saved articles.
    """
    selected = rank_and_select(raw_articles)

    saved_count = 0

    for item in selected:
        # Skip if URL already exists
        exists = db.query(RawArticle).filter(RawArticle.url == item["url"]).first()
        if exists:
            continue

        source = get_or_create_source(
            db,
            name=item["source_name"],
            source_type=item["source_type"],
            url="",  # we can improve this later
            pakistan_focus=item.get("pakistan_focus", False),
            weight=item.get("weight", 1.0)
        )

        article = RawArticle(
            source_id=source.id,
            title=item["title"],
            url=item["url"],
            summary_raw=item.get("summary_raw"),
            content=item.get("content"),
            published_at=item.get("published_at"),
            fetched_at=datetime.now(timezone.utc),
            pakistan_score=item.get("pakistan_score"),
            is_world=item.get("is_world", False)
        )

        db.add(article)
        saved_count += 1

    db.commit()
    return saved_count