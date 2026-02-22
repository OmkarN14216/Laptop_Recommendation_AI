from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import chat
from app.services.laptop_service import laptop_service

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    await laptop_service.initialize()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Laptop Recommendation API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Laptop Recommendation API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}