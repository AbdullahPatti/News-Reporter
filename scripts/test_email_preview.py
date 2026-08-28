from app.database import SessionLocal
from app.models import User
from app.services.email_builder import build_digest_html, get_todays_articles

def main():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("No user found. Register one first.")
            return

        pakistan, world = get_todays_articles(db)
        print(f"Pakistan articles: {len(pakistan)}")
        print(f"World articles: {len(world)}")

        html = build_digest_html(user, pakistan, world)

        # Save preview to file
        with open("digest_preview.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("Preview saved -> digest_preview.html")
        print("Open it in your browser to see the email.")
    finally:
        db.close()

if __name__ == "__main__":
    main()