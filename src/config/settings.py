# src/config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file (if it exists)
# This is great for keeping secrets (like API keys) out of code
load_dotenv()

# --- 1. Base Path Configuration ---
# Use pathlib for clean, OS-agnostic paths
# __file__ is 'src/config/settings.py'
CONFIG_DIR = Path(__file__).resolve().parent
SRC_DIR = CONFIG_DIR.parent
ROOT_DIR = SRC_DIR.parent

# --- 2. Data & Storage Paths ---
# This matches your uploaded file structure
DATA_DIR = SRC_DIR / "data"
PDF_FOLDER = DATA_DIR / "sample_pdfs"

# It's cleaner to put generated files (index, logs) in a top-level folder
# This separates 'source data' (in src/data) from 'artifacts' (in storage/)
STORAGE_DIR = ROOT_DIR / "storage"
INDEX_FILE = STORAGE_DIR / "skb.index"
LOG_FILE = STORAGE_DIR / "skb_api.log"

VISUAL_DATA_DIR = Path("/mnt/v_drive/Codes/SKB/storage/visual_data")

# --- 3. Embedding Model Configuration ---
# The model used to create vectors
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# The dimension of the model. 
# While we can get this from the model, it's good to have for FAISS.
EMBEDDING_DIM = 384

# --- 4. FAISS Index Configuration (The Big One) ---
# This is the "control panel" for your FAISSIndexer
FAISS_CONFIG = {
    # 'ivfpq' is a fast and memory-efficient index.
    # 'flat_l2' is slower but 100% accurate (good for <1M docs)
    "index_type": "ivfpq",
    "nlist": 100,     # Number of clusters (for 'ivfpq')
    "m": 8,           # Number of sub-quantizers (for 'ivfpq')
    "bits": 8,        # Bits per sub-quantizer (for 'ivfpq')
    "metric": "L2",   # L2 (Euclidean) is standard for MiniLM
    "use_gpu": False  # Set to True if you have CUDA and faiss-gpu installed
}

# --- 5. LLM (Ollama) Configuration ---
# Use os.getenv() to read from environment variables first
# This lets you change the host without touching the code
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:4b") # The model to use for chat

# --- 6. API Server Configuration ---
API_HOST = "0.0.0.0"  # Listen on all network interfaces
API_PORT = 8000

# --- 7. Logging Configuration ---
LOG_LEVEL = "INFO" # e.g., "DEBUG", "INFO", "WARNING"

# --- Create directories if they don't exist ---
STORAGE_DIR.mkdir(exist_ok=True)
PDF_FOLDER.mkdir(exist_ok=True)

DOCUMENT_PUBLIC_PATH = "/pdfs"  
# The base URL the frontend uses to serve PDFs.
DOCUMENT_SERVER_URL = f"http://localhost:{API_PORT}{DOCUMENT_PUBLIC_PATH}/"