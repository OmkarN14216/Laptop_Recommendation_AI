# 💻 Laptop Recommendation AI Chatbot

An AI-powered full-stack laptop recommendation system. Chat with the bot, describe your needs, and get the top 3 laptop recommendations scored against your requirements — with live prices from Flipkart and Croma.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=flat&logo=mongodb&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-orange?style=flat)

---

## ✨ Features

- 🤖 AI chatbot collects 10 laptop requirements through natural conversation
- 🎯 Scores all laptops in the database against your needs (0–9 per laptop)
- 💰 Live price scraping from **Flipkart** and **Croma**
- 📊 Returns top 3 matches with specs, score, and direct buy links
- ⚡ Fast inference via Groq API (LLaMA 3.1 8B)

---

## 🗂️ Project Structure

```
LaptopRecommendation/
├── backend/
│   ├── app/
│   │   ├── config.py                      # Environment variables
│   │   ├── database.py                    # MongoDB connection
│   │   ├── main.py                        # FastAPI entry point
│   │   ├── models.py                      # MongoDB document structure
│   │   ├── schemas.py                     # Request/response validation
│   │   ├── routes/
│   │   │   ├── chat.py                    # Chat API endpoints
│   │   │   └── scraper.py                 # Price scraping endpoints
│   │   ├── services/
│   │   │   ├── groq_service.py            # LLM chatbot + intent detection
│   │   │   ├── laptop_service.py          # Scoring & recommendation engine
│   │   │   ├── scraper_service.py         # Orchestrates parallel scraping
│   │   │   ├── cache_service.py           # Scrape result caching
│   │   │   └── scrapers/
│   │   │       ├── __init__.py
│   │   │       ├── flipkart.py            # Flipkart scraper
│   │   │       └── croma.py               # Croma scraper
│   │   └── utils/
│   │       └── helpers.py                 # Session ID, moderation
│   ├── laptop_data2.csv                   # Raw laptop dataset
│   ├── seed_data.py                       # One-time: imports CSV → MongoDB
│   ├── generate_laptop_features.py        # One-time: generates AI features
│   ├── requirements.txt
│   └── .env                               # Secret keys (never commit!)
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ChatInterface.jsx           # Main chat UI
    │   │   ├── MessageBubble.jsx           # Message display
    │   │   ├── LaptopCard.jsx              # Recommendation card
    │   │   ├── LandingPage.jsx             # Landing page
    │   │   └── InputBox.jsx                # Auto-expanding input
    │   ├── services/
    │   │   └── api.js                      # Axios API client
    │   ├── App.jsx
    │   └── main.jsx
    ├── tailwind.config.js
    ├── vite.config.js
    └── package.json
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + Vite |
| Styling | Tailwind CSS v3 |
| HTTP Client | Axios |
| Backend | FastAPI (Python) |
| AI / LLM | Groq API — LLaMA 3.1 8B Instant |
| Database | MongoDB |
| Async DB Driver | Motor |
| Sync DB Driver | PyMongo |
| Validation | Pydantic v2 |
| Scraping | Selenium + WebDriver Manager |

---

## 🔑 Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (local) or MongoDB Atlas account
- Groq API key → [console.groq.com](https://console.groq.com)
- Google Chrome installed (required for Selenium scraping)

---

## 🚀 Running the Project

### 1. Clone the repo

```bash
git clone https://github.com/OmkarN14216/Laptop_Recommendation_AI.git
cd Laptop_Recommendation_AI
```

### 2. Set up environment variables

Create `backend/.env`:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=laptop_recommendation_db
GROQ_API_KEY=your_groq_api_key_here
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

### 3. Start MongoDB

```bash
# Windows (run as administrator)
net start MongoDB

# Mac/Linux
brew services start mongodb-community
```

> If using MongoDB Atlas, skip this step and use your Atlas connection string in `.env`.

### 4. Start the backend

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
✅ Connected to MongoDB
INFO: Application startup complete.
```

### 5. Start the frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open → **http://localhost:5173**

---

## 🗄️ Database Setup (First Time Only)

> Only needed if the database is empty or you're setting up fresh.

```bash
cd backend
venv\Scripts\activate

# Step 1: Import laptop data from CSV
python seed_data.py

# Step 2: Generate AI features for each laptop (takes a few minutes)
python generate_laptop_features.py
```

`generate_laptop_features.py` uses Groq AI to classify each laptop's specs into `low / medium / high` across 9 features and stores them in MongoDB.

> ✅ Once done, you don't need to run these again unless you reset the database.

---

## 💬 How It Works

```
1. User opens app → new session created → bot greets user
2. Bot collects 10 requirements through conversation:
   GPU intensity, Processing speed, RAM capacity, Storage capacity,
   Storage type, Display quality, Display size, Portability,
   Battery life, Budget (INR)
3. Once all 10 are collected → bot outputs requirements dictionary
4. Backend detects intent confirmation (pure Python, no extra LLM call)
5. All laptops within budget are scored 0–9
6. Top 3 laptops returned with specs and match score
7. Live prices scraped in parallel from Flipkart + Croma
8. Laptop cards displayed with prices and direct buy links
```

---

## 📊 Scoring System

```
Mapping:  low = 0,  medium = 1,  high = 2

For each of 9 features (excluding budget):
  if laptop_feature_value >= user_requirement_value → +1 point

Max score = 9  |  Min accepted = 5
```

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

## 🐛 Common Issues

**CORS error on frontend**
Make sure `ALLOWED_ORIGINS` in `.env` includes your frontend port (5173 or 5174).

**`AttributeError: 'NoneType' object has no attribute 'laptops'`**
MongoDB isn't connected. Check `MONGODB_URL` in `.env` and ensure MongoDB is running.

**No recommendations showing**
Run `generate_laptop_features.py` — laptops need AI features to be scored.

**404 on chat message after backend restart**
Sessions are stored in memory. Refresh the frontend page to start a new session.

**Scraper returns no results**
Google Chrome must be installed. WebDriver Manager auto-downloads the matching ChromeDriver.

**Bot asks too many / too few questions**
Edit the system prompt in `backend/app/services/groq_service.py` → `initialize_conversation()`.

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/.env` | API keys and config |
| `backend/app/services/groq_service.py` | Chatbot prompt + intent detection |
| `backend/app/services/laptop_service.py` | Scoring algorithm |
| `backend/app/services/scrapers/flipkart.py` | Flipkart price scraper |
| `backend/app/services/scrapers/croma.py` | Croma price scraper |
| `backend/app/routes/chat.py` | Chat API + recommendation logic |
| `frontend/src/components/ChatInterface.jsx` | Main UI logic |
| `frontend/src/components/LaptopCard.jsx` | Laptop card design |
| `frontend/src/services/api.js` | Backend URL config |
