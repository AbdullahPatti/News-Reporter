from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from app.models import User, RawArticle
from app.config import settings
from app.auth.jwt import create_access_token
from app.utils.helpers import format_relative_time

env = Environment(
    loader=FileSystemLoader("app/templates/email"),
    autoescape=select_autoescape(["html", "xml"])
)

PKT = ZoneInfo("Asia/Karachi")


def _base_url() -> str:
    return settings.APP_BASE_URL.rstrip("/")


def build_digest_html(
    user: User,
    pakistan_articles: List[RawArticle],
    world_articles: List[RawArticle],
    base_url: str | None = None
) -> str:
    """
    Renders the daily digest HTML email for a specific user.
    """
    template = env.get_template("daily_digest.html")
    origin = (base_url or _base_url()).rstrip("/")

    now = datetime.now(PKT)
    date_str = now.strftime("%A, %d %B %Y")

    unsubscribe_token = create_access_token(
        data={"sub": str(user.id), "type": "unsubscribe"},
        expires_delta=timedelta(days=90),
    )

    html = template.render(
        user=user,
        pakistan_articles=pakistan_articles,
        world_articles=world_articles,
        date_str=date_str,
        preferences_url=f"{origin}/dashboard/preferences",
        unsubscribe_url=f"{origin}/unsubscribe?token={unsubscribe_token}",
    )
    return html


def get_todays_articles(db, max_pakistan: int = 8, max_world: int = 4):
    """
    Fetch the best summarized articles from the last 24-36 hours.
    """
    cutoff = datetime.now(PKT) - timedelta(hours=36)

    pakistan = (
        db.query(RawArticle)
        .options(joinedload(RawArticle.source))
        .filter(
            RawArticle.llm_summary.isnot(None),
            RawArticle.is_world == False,
            RawArticle.fetched_at >= cutoff
        )
        .order_by(desc(RawArticle.pakistan_score), desc(RawArticle.fetched_at))
        .limit(max_pakistan)
        .all()
    )

    world = (
        db.query(RawArticle)
        .options(joinedload(RawArticle.source))
        .filter(
            RawArticle.llm_summary.isnot(None),
            RawArticle.is_world == True,
            RawArticle.fetched_at >= cutoff
        )
        .order_by(desc(RawArticle.fetched_at))
        .limit(max_world)
        .all()
    )

    return pakistan, world


def get_landing_preview(db, limit: int = 2) -> list[dict]:
    """Pick a couple of recent real stories for the public homepage."""
    pakistan, world = get_todays_articles(db, max_pakistan=1, max_world=1)
    selected = []
    if pakistan:
        selected.append(pakistan[0])
    if world:
        selected.append(world[0])

    if len(selected) < limit:
        extra = (
            db.query(RawArticle)
            .options(joinedload(RawArticle.source))
            .filter(RawArticle.llm_summary.isnot(None))
            .order_by(desc(RawArticle.fetched_at))
            .limit(limit)
            .all()
        )
        seen = {a.id for a in selected}
        for article in extra:
            if article.id not in seen:
                selected.append(article)
            if len(selected) >= limit:
                break

    preview = []
    for article in selected[:limit]:
        source_name = article.source.name if article.source else "Source"
        preview.append({
            "title": article.title,
            "summary": article.llm_summary or article.summary_raw or "",
            "url": article.url,
            "source": source_name,
            "section": "World" if article.is_world else "Pakistan",
            "time_ago": format_relative_time(article.published_at or article.fetched_at),
        })
    return preview
