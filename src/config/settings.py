# src/config/settings.py
"""
This module serves as the single source of truth for system-wide configuration parameters.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# __file__ = src/config/settings.py
CONFIG_DIR = Path(__file__).resolve().parent
SRC_DIR = CONFIG_DIR.parent
ROOT_DIR = SRC_DIR.parent

# Source data (checked into repo or mounted volume)
DATA_DIR = SRC_DIR / "data"
PDF_FOLDER = DATA_DIR / "sample_pdfs"

# Generated artifacts (indexes, visuals, logs)
STORAGE_DIR = ROOT_DIR / "storage"
VISUAL_DATA_DIR = STORAGE_DIR / "visual_data"
INDEX_FILE = STORAGE_DIR / "skb.index"
LOG_FILE = STORAGE_DIR / "skb_api.log"

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)

EMBEDDING_DIM = int(os.getenv(
    "EMBEDDING_DIM",
    384
))


FAISS_CONFIG = {
    # Index type: flat_l2 | ivf | ivfpq | hnsw
    "index_type": os.getenv("FAISS_INDEX_TYPE", "ivfpq"),

    # IVF / IVFPQ parameters
    "nlist": int(os.getenv("FAISS_NLIST", 100)),
    "m": int(os.getenv("FAISS_M", 8)),
    "bits": int(os.getenv("FAISS_BITS", 8)),

    # Distance metric: L2 or IP
    "metric": os.getenv("FAISS_METRIC", "L2"),

    # GPU usage
    "use_gpu": os.getenv("FAISS_USE_GPU", "false").lower() == "true",
}

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "llama3:instruct"
)

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

USE_MONGODB = os.getenv(
    "USE_MONGODB",
    "true"
).lower() == "true"

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017"
)

MONGO_DB_NAME = os.getenv(
    "MONGO_DB_NAME",
    "skb"
)

DOCUMENT_PUBLIC_PATH = "/pdfs"
DOCUMENT_SERVER_URL = f"http://localhost:{API_PORT}{DOCUMENT_PUBLIC_PATH}/"

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
PDF_FOLDER.mkdir(parents=True, exist_ok=True)
VISUAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
