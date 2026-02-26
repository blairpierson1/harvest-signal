from dotenv import load_dotenv

load_dotenv()  # Load .env file before anything else reads os.environ

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router

app = FastAPI(title="Harvest Signal API", version="1.0.0")

# CORS configuration – allow all origins so the public API works from any frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
