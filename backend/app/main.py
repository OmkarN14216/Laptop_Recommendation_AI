from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import chat, scraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(title="Laptop Recommendation API")

# CORS
origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
logger.info(f"Allowed CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await connect_to_mongo()  # laptop_service uses _get_db() so no initialize() needed

@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["scraper"])

@app.get("/health")
async def health():
    return {"status": "ok"}