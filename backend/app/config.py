import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
CARDS_DIR = DATA_DIR / "id_cards"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
CARDS_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'attendai.db'}")
SECRET_KEY = os.getenv("SECRET_KEY", "attendai_offline_super_secret_key_2026_apex")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours for local deployment

FACE_SIMILARITY_THRESHOLD = 0.65  # 65% match required for face verification
ID_CARD_CONFIDENCE_THRESHOLD = 0.60
