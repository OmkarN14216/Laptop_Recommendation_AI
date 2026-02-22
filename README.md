# 💻 Laptop Recommendation AI Chatbot

A full-stack AI-powered laptop recommendation system. The chatbot asks users about their requirements, collects 10 features, and recommends the top 3 laptops from a MongoDB database using a scoring algorithm.

---

## 🗂️ Project Structure

```
LaptopRecommendation/
├── backend/
│   ├── app/
│   │   ├── config.py               # Environment variables loader
│   │   ├── database.py             # MongoDB connection
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── models.py               # MongoDB document structure (reference)
│   │   ├── schemas.py              # API request/response validation
│   │   ├── routes/
│   │   │   └── chat.py             # Chat API endpoints
│   │   ├── services/
│   │   │   ├── groq_service.py     # Groq AI chatbot logic
│   │   │   └── laptop_service.py   # Laptop scoring & recommendation engine
│   │   └── utils/
│   │       └── helpers.py          # Session ID generation, moderation
│   ├── venv/                       # Python virtual environment
│   ├── laptop_data2.csv            # Raw laptop data
│   ├── seed_data.py                # One-time script: import CSV to MongoDB
│   ├── generate_laptop_features.py # One-time script: generate AI features
│   ├── requirements.txt            # Python dependencies
│   └── .env                        # Secret keys (never commit this!)
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ChatInterface.jsx    # Main chat UI (parent component)
    │   │   ├── MessageBubble.jsx    # Individual message display
    │   │   ├── LaptopCard.jsx       # Laptop recommendation card
    │   │   └── InputBox.jsx         # Message input field
    │   ├── services/
    │   │   └── api.js               # Axios API client (calls backend)
    │   ├── App.jsx                  # Root React component
    │   ├── App.css                  # Global styles
    │   └── main.jsx                 # React app bootstrap
    ├── tailwind.config.js           # Tailwind CSS config
    ├── postcss.config.js            # PostCSS config (required for Tailwind)
    ├── vite.config.js               # Vite build tool config
    └── package.json                 # Frontend dependencies
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite |
| Styling | Tailwind CSS v3 |
| HTTP Client | Axios |
| Backend | FastAPI (Python) |
| AI/LLM | Groq API (llama-3.1-8b-instant) |
| Database | MongoDB (local or Atlas) |
| Async DB Driver | Motor |
| Sync DB Driver | PyMongo |
| Validation | Pydantic v2 |

---

## 🔑 Prerequisites

Make sure these are installed on your machine:

- Python 3.10+
- Node.js 18+
- MongoDB (local) OR MongoDB Atlas account
- Groq API key → Get from https://console.groq.com

---

## 🚀 How to Run the Project

### Step 1: Start MongoDB

**If using local MongoDB:**
```bash
# Windows (run as administrator)
net start MongoDB

# Mac/Linux
brew services start mongodb-community
# OR
sudo systemctl start mongod
```

**If using MongoDB Atlas:**
- Just make sure your `.env` has the correct Atlas connection string
- No need to start anything locally

---

### Step 2: Start the Backend

```bash
# Navigate to backend folder
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see:**
```
✅ Connected to MongoDB
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

### Step 3: Start the Frontend

Open a **new terminal** (keep backend running):

```bash
# Navigate to frontend folder
cd frontend

# Start the React dev server
npm run dev
```

**You should see:**
```
VITE v5.x.x  ready in 500ms
➜  Local:   http://localhost:5173/
```

---

### Step 4: Open the App

Go to → **http://localhost:5173**

The chatbot will greet you and start asking questions!

---

## 🗄️ Database Setup (First Time Only)

> ⚠️ Only do this if the database is empty or you need to reset it.

### Step 1: Seed laptop data from CSV

```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate on Mac/Linux
python seed_data.py
```

This will:
- Clear existing laptop data
- Import all laptops from `laptop_data2.csv`
- **NOT generate features yet** (done in next step)

### Step 2: Generate AI features for each laptop

```bash
python generate_laptop_features.py
```

This will:
- Use Groq AI to analyze each laptop's specs
- Classify 9 features as `low`, `medium`, or `high`
- Store features in MongoDB
- Takes a few minutes (2 second delay between each laptop to avoid rate limiting)

> ✅ After this, the database is ready. You don't need to run these scripts again unless you reset the database.

---

## 🔧 Environment Variables

The `.env` file lives in `/backend/.env`. Make sure it has:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=laptop_recommendation_db
GROQ_API_KEY=your_groq_api_key_here
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:5173
```

**To get your Groq API key:**
1. Go to https://console.groq.com
2. Sign in / Sign up
3. Go to API Keys → Create new key
4. Copy and paste into `.env`

---

## 🛑 How to Stop the Project

- **Backend:** Press `Ctrl + C` in the backend terminal
- **Frontend:** Press `Ctrl + C` in the frontend terminal
- **MongoDB (local):** `net stop MongoDB` (Windows) or `brew services stop mongodb-community` (Mac)

---

## 🐛 Common Issues & Fixes

### ❌ Backend won't start - "Module not found"
```bash
# Make sure venv is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### ❌ MongoDB connection error
```bash
# Check if MongoDB is running (local)
net start MongoDB  # Windows

# Or check your Atlas connection string in .env
# Make sure IP 0.0.0.0/0 is whitelisted in Atlas
```

### ❌ Groq API error
- Check your `GROQ_API_KEY` in `.env`
- Make sure the key is valid at https://console.groq.com
- Check your Groq usage limits

### ❌ Frontend not loading / CORS error
- Make sure backend is running on port 8000
- Make sure frontend is running on port 5173
- Check `FRONTEND_URL` in `.env` matches your frontend URL

### ❌ 404 on chat message
- Refresh the frontend page (Ctrl+Shift+R)
- The session may have expired when backend restarted
- Sessions are stored in-memory, so backend restart clears them

### ❌ No recommendations showing
- Run `python generate_laptop_features.py` if not done yet
- Check backend terminal for scoring logs
- Verify laptops have `laptop_feature` field in MongoDB

---

## 🔁 Reset Database (If Needed)

```bash
cd backend
venv\Scripts\activate
python clear_and_reseed.py      # Clears + reseeds data
python generate_laptop_features.py  # Regenerates AI features
```

---

## 🧪 Test the API

Open Swagger UI at: **http://localhost:8000/docs**

Test endpoints:
1. `POST /api/chat/session` → Creates new session
2. `POST /api/chat/message` → Send message with `session_id`
3. `GET /api/chat/session/{id}` → View session data

---

## 💬 How the Chatbot Works

```
1. User opens app → New session created → Bot greets user
2. Bot asks about 10 features one by one:
   - GPU Intensity
   - Processing Speed
   - RAM Capacity
   - Storage Capacity
   - Storage Type
   - Display Quality
   - Display Size
   - Portability
   - Battery Life
   - Budget (INR)
3. After collecting all 10 → Bot outputs user profile dictionary
4. Backend detects intent confirmation
5. Backend scores all laptops within budget (0-9 points each)
6. Top 3 laptops returned and displayed as cards
```

---

## 📊 Scoring System

Each laptop is scored out of 9 (one point per feature):

```
low = 0, medium = 1, high = 2

For each feature:
  if laptop_feature >= user_requirement → score + 1

Max score = 9 (all features match)
Min accepted score = 5 (at least 5 features match)
```

---

## 📁 Key Files Quick Reference

| File | What to edit |
|------|-------------|
| `backend/.env` | API keys, DB URL |
| `backend/app/services/groq_service.py` | Chatbot prompts, AI behavior |
| `backend/app/services/laptop_service.py` | Scoring algorithm |
| `backend/app/routes/chat.py` | API endpoints, recommendation display |
| `frontend/src/components/ChatInterface.jsx` | Main UI logic |
| `frontend/src/components/LaptopCard.jsx` | Laptop card design |
| `frontend/src/services/api.js` | Backend URL config |

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
