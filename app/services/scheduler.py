from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, DigestLog
from app.services.news_fetcher import fetch_all_sources
from app.services.article_saver import save_articles
from app.services.summarizer import summarize_pending_articles
from app.services.email_builder import build_digest_html, get_todays_articles
from app.services.email_sender import send_digest_email

PKT = ZoneInfo("Asia/Karachi")
scheduler = BackgroundScheduler(timezone=PKT)


def pre_fetch_and_summarize():
    """
    Runs early morning (around 4:30–5:30 AM).
    Fetches news + generates summaries so they are ready before 6 AM.
    """
    print(f"[{datetime.now(PKT)}] Starting pre-fetch & summarize job...")
    db = SessionLocal()
    try:
        # 1. Fetch latest articles
        articles = fetch_all_sources()
        print(f"Fetched {len(articles)} articles")

        # 2. Save new ones
        saved = save_articles(db, articles)
        print(f"Saved {saved} new articles")

        # 3. Summarize pending ones
        summarized = summarize_pending_articles(db, limit=20)
        print(f"Summarized {summarized} articles")

    except Exception as e:
        print(f"Pre-fetch job failed: {e}")
    finally:
        db.close()


def run_morning_digest():
    """
    Runs every 15–20 minutes between 6–10 AM.
    Sends digests only to users whose preferred_hour matches current hour
    and who haven't received today's digest yet.
    """
    now = datetime.now(PKT)
    current_hour = now.hour

    # Only run inside the delivery window
    if current_hour < 6 or current_hour > 10:
        return

    print(f"[{now}] Running morning digest check for hour {current_hour}...")

    db = SessionLocal()
    try:
        today_start = datetime.combine(now.date(), datetime.min.time(), tzinfo=PKT)

        # Users who want the digest at this hour and haven't received it today
        users = (
            db.query(User)
            .filter(
                User.is_active == True,
                User.preferred_hour == current_hour,
                (User.last_digest_sent_at == None) | (User.last_digest_sent_at < today_start)
            )
            .all()
        )

        if not users:
            print("No users to send at this hour.")
            return

        print(f"Found {len(users)} users for hour {current_hour}")

        # Get today's articles once (shared for all users)
        pakistan_articles, world_articles = get_todays_articles(db)

        if not pakistan_articles and not world_articles:
            print("No articles available to send.")
            return

        for user in users:
            try:
                html = build_digest_html(user, pakistan_articles, world_articles)
                subject = f"News Reporter • {now.strftime('%d %b')} – Top stories for you"

                msg_id = send_digest_email(user.email, subject, html)

                # Log the attempt
                log = DigestLog(
                    user_id=user.id,
                    status="sent" if msg_id else "failed",
                    subject=subject,
                    article_count=len(pakistan_articles) + len(world_articles),
                    provider_message_id=msg_id,
                    error_message=None if msg_id else "Failed to send"
                )
                db.add(log)

                if msg_id:
                    user.last_digest_sent_at = now
                    print(f"  ✓ Sent to {user.email}")
                else:
                    print(f"  ✗ Failed to send to {user.email}")

                db.commit()

            except Exception as e:
                print(f"  ✗ Error for {user.email}: {e}")
                db.rollback()
                # Still log the failure
                try:
                    log = DigestLog(
                        user_id=user.id,
                        status="failed",
                        error_message=str(e)
                    )
                    db.add(log)
                    db.commit()
                except:
                    db.rollback()

    except Exception as e:
        print(f"Morning digest job failed: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start all scheduled jobs."""
    # Pre-fetch job: every day at 4:45 AM PKT
    scheduler.add_job(
        pre_fetch_and_summarize,
        trigger=CronTrigger(hour=4, minute=45, timezone=PKT),
        id="pre_fetch",
        replace_existing=True
    )

    # Morning digest job: every 15 minutes from 6:00 to 10:45
    scheduler.add_job(
        run_morning_digest,
        trigger=CronTrigger(minute="0,15,30,45", hour="6-10", timezone=PKT),
        id="morning_digest",
        replace_existing=True
    )

    scheduler.start()
    print("Scheduler started successfully.")