from app.database import SessionLocal
from app.services.summarizer import summarize_pending_articles

def main():
    db = SessionLocal()
    try:
        count = summarize_pending_articles(db, limit=12)
        print(f"\nSuccessfully summarized {count} articles")
    finally:
        db.close()

if __name__ == "__main__":
    main()