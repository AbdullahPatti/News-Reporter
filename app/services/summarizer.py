from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from typing import Optional
import time

from app.config import settings
from app.models import RawArticle

client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None

MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = (
    "You are a professional Pakistani news editor. "
    "Write neutral, factual summaries only. "
    "Do not add opinions, speculation, or extra commentary."
)

USER_PROMPT_TEMPLATE = """Summarize the following article in 2–3 clear sentences (maximum 80 words).
Focus on facts, key people, places and consequences.

Title: {title}

Content: {content}
"""


def summarize_text(title: str, content: str, max_retries: int = 3) -> Optional[str]:
    if not client:
        print("GEMINI_API_KEY not set")
        return None

    prompt = USER_PROMPT_TEMPLATE.format(
        title=title,
        content=(content or "")[:2200]
    )

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.25,
                    max_output_tokens=200,
                ),
            )

            if response and response.text:
                summary = response.text.strip()
                if len(summary) > 40:
                    return summary

            print("  → Empty or low-quality response")
            return None

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait = 35 + (attempt * 15)
                print(f"  → Rate limited. Waiting {wait}s (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait)
                continue
            else:
                print(f"  → Gemini error: {e}")
                return None

    print("  → Failed after retries")
    return None


def summarize_pending_articles(db: Session, limit: int = 12) -> int:
    """
    Summarize articles that still need an llm_summary.
    Commits after every article to avoid Neon SSL timeout.
    """
    articles = (
        db.query(RawArticle)
        .filter(RawArticle.llm_summary.is_(None))
        .order_by(RawArticle.pakistan_score.desc())
        .limit(limit)
        .all()
    )

    if not articles:
        print("No articles pending summarization.")
        return 0

    count = 0
    for i, article in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] {article.title[:70]}...")

        summary = summarize_text(
            article.title,
            article.content or article.summary_raw or ""
        )

        if summary:
            article.llm_summary = summary
            try:
                db.commit()          # ← commit immediately
                count += 1
                print(f"  ✓ Saved ({len(summary)} chars)")
            except Exception as e:
                print(f"  ✗ Failed to save: {e}")
                db.rollback()
        else:
            print("  ✗ Skipped")

        # Respect free-tier rate limits
        if i < len(articles):
            time.sleep(18)

    return count