# 📰 Daily Digest – AI News Aggregator

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green)
![Gemini](https://img.shields.io/badge/AI-Google_Gemini-orange)
![Status](https://img.shields.io/badge/Status-Live-success)

**Live Demo:** [https://dailydigest-jy4r.onrender.com](https://dailydigest-jy4r.onrender.com)

An end-to-end Generative AI news aggregator that collects top Pakistani and major worldwide news, generates concise neutral summaries using **Google Gemini**, and delivers a clean personalized HTML email digest every morning between **6–10 AM Pakistan Standard Time (PKT)**.

---

## 🌟 Project Vision & Significance

Most people consume news through noisy social media feeds or long articles. Daily Digest solves this by delivering a short, high-signal, AI-curated morning briefing.

**Why this project matters:**

- It is a complete real-world Generative AI product (not just a demo or notebook)
- Runs entirely on free tiers (Neon, Render, Gemini, Resend)
- Serves real users with fully automated daily delivery
- Combines modern backend engineering, AI, scheduling, email systems, and clean UI
- Strong portfolio piece:  
  *“Built and deployed an end-to-end AI news agent that delivers personalized daily digests to real users.”*

---

## ✨ Key Features

- **AI-Powered Summaries** – Google Gemini (`gemini-3.5-flash-lite`) generates neutral, factual 2–3 sentence summaries
- **Pakistan-first Ranking** – Custom scoring algorithm prioritizes local relevance while still including major world stories
- **Personalized Delivery** – Users choose their preferred delivery hour (6 AM – 10 AM PKT)
- **Fully Automated Pipeline** – Fetches → Ranks → Summarizes → Emails with zero manual work
- **Secure Authentication** – Email + password registration and JWT-based login
- **Clean Web Interface** – Server-rendered with Jinja2 + Tailwind (minimal, modern design)
- **Professional Email Digests** – Beautiful HTML emails delivered via Resend
- **Cloud Native** – PostgreSQL on Neon + Dockerized deployment on Render
- **Keep-Alive System** – External cron pings prevent the free-tier service from sleeping

---

## 🛠️ Tech Stack

| Layer              | Technology                          | Notes |
|--------------------|-------------------------------------|-------|
| Backend            | FastAPI + Uvicorn                   | Modern async Python |
| Database           | PostgreSQL (Neon)                   | Free serverless Postgres |
| ORM & Migrations   | SQLAlchemy 2.0 + Alembic            | Clean schema management |
| Authentication     | JWT (python-jose) + passlib/bcrypt  | Secure login |
| Frontend           | Jinja2 + Tailwind CSS               | Zero build step |
| AI Summaries       | Google GenAI (`gemini-3.5-flash-lite`) | Free-tier friendly |
| Email              | Resend                              | 3,000 emails/month free |
| News Sources       | RSS (Dawn, Tribune, BBC, Al Jazeera, Reuters, etc.) | Reliable & free |
| Scheduler          | APScheduler                         | In-process background jobs |
| Deployment         | Docker + Render                     | Free tier + cron keep-alive |
| Secrets            | Environment Variables               | Never committed to Git |

---

## 🏗️ System Architecture

```
User Browser
     ↓
FastAPI (Jinja2 + Tailwind)
     ↓
Auth Layer (JWT)
     ↓
PostgreSQL (Neon)
     ↑
Background Worker (APScheduler)
  1. Fetch news from RSS sources
  2. Rank by Pakistan relevance + recency
  3. Deduplicate
  4. Summarize with Gemini (cached per article)
  5. Build clean HTML email
  6. Send via Resend at each user’s preferred hour
```

### Daily Automation Flow

- **4:45 AM PKT** → Pre-fetch latest articles + generate summaries
- **6:00 – 10:45 AM PKT** → Every 15 minutes the system checks for users whose preferred hour matches the current hour and sends their digest

New users and preference changes are automatically respected from the next day.

---

## 📊 Database Schema (Core Tables)

| Table            | Purpose |
|------------------|--------|
| `users`          | Accounts, preferred delivery hour, last digest timestamp |
| `sources`        | Configurable news sources (RSS) |
| `raw_articles`   | Cached articles + AI summaries (avoids re-summarizing) |
| `digest_logs`    | Delivery history and failure tracking |

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/AbdullahPatti/News-Reporter.git
cd News-Reporter
```

### 2. Environment Variables
Create a `.env` file in the root:

```env
SECRET_KEY=your-long-random-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENVIRONMENT=development

DATABASE_URL=postgresql://user:password@host/db?sslmode=require

GEMINI_API_KEY=AIza...
RESEND_API_KEY=re_...
EMAIL_FROM=Daily Digest <onboarding@resend.dev>

INTERNAL_API_KEY=some-random-string
```

### 3. Local Development
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### 4. Docker
```bash
docker build -t daily-digest .
docker run -p 8000:8000 --env-file .env daily-digest
```

---

## ⚙️ How the Automation Works

1. **Pre-fetch Job (early morning)**  
   Pulls RSS feeds → scores articles → saves new ones → generates Gemini summaries

2. **Morning Digest Job**  
   Finds eligible users → builds personalized HTML email → sends via Resend → logs the result

3. **Manual Triggers** (for testing)  
   - `POST /internal/run-prefetch`  
   - `POST /internal/run-digest`  
   (Protected by `INTERNAL_API_KEY`)

---

## 🌐 Deployment

| Component     | Service   | Notes |
|---------------|-----------|-------|
| Database      | Neon      | Free serverless PostgreSQL |
| Application   | Render    | Docker deployment |
| Keep-alive    | cron-job.org | Pings `/health` every 10–12 minutes |
| Email         | Resend    | Free tier (3,000 emails/month) |
| AI            | Google Gemini | Free tier |

**Important:** Free Render instances sleep after 15 minutes of inactivity. A free external cron job is used to keep the service awake.

---

## 📈 Future Improvements

- Article images inside emails
- YouTube channel integration
- Weekly digest option
- More advanced personalization
- Admin analytics dashboard
- Email verification flow
- Better mobile polish

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to open an issue or submit a pull request.

---

## 📝 License

This project is licensed under the **MIT License**.

---

**Built as a real product, not just a demo.**  
Designed to be used every morning by real people.
```

The file is ready. You can download it here:

**[Download README.md](https://file-url-will-be-provided-by-system)** 

(In this environment the file is saved at `/home/workdir/artifacts/README.md`)

Would you like me to also generate a shorter version or a version with more technical architecture diagrams?