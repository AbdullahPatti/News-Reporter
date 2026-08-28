from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models import User, RawArticle

# Setup Jinja2 for email templates
env = Environment(
    loader=FileSystemLoader("app/templates/email"),
    autoescape=select_autoescape(["html", "xml"])
)

PKT = ZoneInfo("Asia/Karachi")


def build_digest_html(
    user: User,
    pakistan_articles: List[RawArticle],
    world_articles: List[RawArticle],
    base_url: str = "http://127.0.0.1:8000"
) -> str:
    """
    Renders the daily digest HTML email for a specific user.
    """
    template = env.get_template("daily_digest.html")

    now = datetime.now(PKT)
    date_str = now.strftime("%A, %d %B %Y")

    html = template.render(
        user=user,
        pakistan_articles=pakistan_articles,
        world_articles=world_articles,
        date_str=date_str,
        preferences_url=f"{base_url}/dashboard/preferences",
        unsubscribe_url=f"{base_url}/unsubscribe?email={user.email}",  # simple for now
    )
    return html


def get_todays_articles(db, max_pakistan: int = 8, max_world: int = 4):
    """
    Fetch the best summarized articles from the last 24-36 hours.
    """
    from datetime import timedelta
    from sqlalchemy import desc

    cutoff = datetime.now(PKT) - timedelta(hours=36)

    # Pakistan articles
    pakistan = (
        db.query(RawArticle)
        .filter(
            RawArticle.llm_summary.isnot(None),
            RawArticle.is_world == False,
            RawArticle.fetched_at >= cutoff
        )
        .order_by(desc(RawArticle.pakistan_score), desc(RawArticle.fetched_at))
        .limit(max_pakistan)
        .all()
    )

    # World articles
    world = (
        db.query(RawArticle)
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