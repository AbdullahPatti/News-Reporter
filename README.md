# 📰 AI News Aggregator (Daily Digest)

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green)
![Gemini](https://img.shields.io/badge/AI-Google_Gemini-orange)

An intelligent, fully automated AI News Aggregator that fetches the latest news from top sources, summarizes them using **Google's Gemini AI**, and delivers a beautifully curated daily email digest to users at their preferred time.

---

## 🌟 Features

- **🤖 AI-Powered Summaries**: Automatically generates concise, factual, and neutral summaries of long news articles using `gemini-3.5-flash-lite`.
- **⏰ Smart Scheduling**: Fully autonomous background tasks (`APScheduler`) that pre-fetch news early in the morning and dispatch emails exactly when users want them (between 6 AM and 10 AM).
- **🌍 Focused Content**: Custom ranking algorithm that prioritizes Pakistan-focused news alongside major global headlines.
- **✉️ Seamless Delivery**: Automated email dispatching powered by the **Resend API**.
- **🔒 Secure Authentication**: User registration, JWT-based authentication, and password reset functionalities included.
- **🐳 Docker Ready**: Comes with a fully configured `Dockerfile` that handles dependencies, real-time logging, and automated database migrations.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI
- **Database**: PostgreSQL, SQLAlchemy ORM, Alembic (Migrations)
- **AI Integration**: Google GenAI SDK (`gemini-3.5-flash-lite`)
- **Email Service**: Resend API
- **Task Scheduling**: APScheduler
- **Frontend/Templates**: Jinja2, TailwindCSS

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/AbdullahPatti/News-Reporter.git
cd "News-Reporter"
```

### 2. Set Up Environment Variables
Create a `.env` file in the root directory based on `.env.example`:
```ini
SECRET_KEY=your_super_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/news_db
GEMINI_API_KEY=your_gemini_api_key
RESEND_API_KEY=your_resend_api_key
APP_BASE_URL=http://localhost:8000
ENVIRONMENT=development
```

### 3. Run with Docker (Recommended)
The easiest way to run the application is using Docker. The provided Dockerfile will automatically install dependencies, run database migrations, and start the app.
```bash
docker build -t ai-news-aggregator .
docker run -p 8000:8000 --env-file .env ai-news-aggregator
```

### 4. Local Development (Without Docker)
Make sure you have PostgreSQL running and Python 3.12 installed.
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload
```

---

## ⚙️ How It Works (The Automation Pipeline)

1. **4:45 AM (Pre-fetch)**: The background scheduler wakes up, parses RSS feeds from sources like Dawn, The News, Express Tribune, BBC, Al Jazeera, and Reuters. 
2. **AI Processing**: The custom ranking algorithm filters the best articles. Gemini AI processes the pending articles and generates 2-3 sentence summaries.
3. **6:00 AM - 10:00 AM (Delivery)**: Every 15 minutes, the system checks for users who have requested their digest for the current hour. If a match is found, an elegant HTML email is constructed and dispatched via Resend.

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/AbdullahPatti/News-Reporter/issues).

## 📝 License
This project is licensed under the MIT License.
