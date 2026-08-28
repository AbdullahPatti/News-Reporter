from datetime import datetime
from zoneinfo import ZoneInfo
from app.database import SessionLocal
from app.models import User
from app.services.email_builder import build_digest_html, get_todays_articles
from app.services.email_sender import send_digest_email

PKT = ZoneInfo("Asia/Karachi")

def main():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("No user found.")
            return

        pakistan, world = get_todays_articles(db)
        html = build_digest_html(user, pakistan, world)

        today = datetime.now(PKT).strftime("%d %b")
        subject = f"News Reporter • {today} – Top stories for you"

        print(f"Sending to {user.email}...")
        msg_id = send_digest_email(user.email, subject, html)

        if msg_id:
            print(f"Email sent successfully! Message ID: {msg_id}")
        else:
            print("Failed to send email.")
    finally:
        db.close()

if __name__ == "__main__":
    main()