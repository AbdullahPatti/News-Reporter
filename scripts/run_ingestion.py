from app.database import SessionLocal
from app.services.news_fetcher import fetch_all_sources
from app.services.article_saver import save_articles

def main():
    print("Fetching articles...")
    articles = fetch_all_sources()
    print(f"Fetched {len(articles)} articles")

    db = SessionLocal()
    try:
        saved = save_articles(db, articles)
        print(f"Saved {saved} new articles to database")
    finally:
        db.close()

if __name__ == "__main__":
    main()