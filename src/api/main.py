# chatbot_api.py
import os
import time
from fastapi import (
    FastAPI, Depends, HTTPException, Request,
    UploadFile, File, BackgroundTasks
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
import shutil 

from chatbot.chatbot_service import ChatbotService
from src.index.faiss_indexer import FAISSIndexer
from chatbot.llm_interface import LocalLLMInterface
from src.utils.pdf_extractor import PDFExtractor
from fastapi.staticfiles import StaticFiles
from src.config.settings import (
    PDF_FOLDER, INDEX_FILE, EMBEDDING_MODEL, FAISS_CONFIG
)

def _build_index_pipeline() -> (FAISSIndexer, int):
    """
    Runs the full E-T-L pipeline: Extract, Transform (embed), Load (into index).
    Returns a newly built and saved indexer.
    """
    print("--- Rouge Coder: Index Rebuild Initiated ---")
    start_time = time.time()

    # 1. Initialize a NEW, blank indexer
    # We use the config from our settings file
    indexer = FAISSIndexer(
        embedding_model_name=EMBEDDING_MODEL,
        index_config=FAISS_CONFIG
    )

    # 2. Extract
    print(f"Extracting data from {PDF_FOLDER}...")
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        print(f"Created PDF folder: {PDF_FOLDER}")
        return indexer, 0 # Return empty index

    extractor = PDFExtractor()
    semantic_chunks, _ = extractor.extract_from_folder(PDF_FOLDER)
    print(f"Found {len(semantic_chunks)} semantic chunks.")

    # 3. Add and Train
    if semantic_chunks:
        indexer.add_chunks(semantic_chunks)

        # 4. Save
        print(f"Saving index to {INDEX_FILE}...")
        os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
        indexer.save(INDEX_FILE)

    total_time = time.time() - start_time
    print(f"--- Index build complete in {total_time:.2f}s ---")
    return indexer, len(semantic_chunks)

# --- 2. Lifespan Manager (Loads models on startup) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs ONCE, before the server starts
    print("--- Rouge Coders: API Boot Phase ---")

    # 1. Build or Load the Index
    if os.path.exists(INDEX_FILE):
        try:
            print(f"Loading existing index from {INDEX_FILE}...")
            indexer = FAISSIndexer(embedding_model_name=EMBEDDING_MODEL)
            indexer.load(INDEX_FILE)
            print("Index loaded successfully.")
        except Exception as e:
            print(f"Error loading index: {e}. Re-building...")
            indexer, _ = _build_index_pipeline()
    else:
        print("No index file found. Building new index...")
        indexer, _ = _build_index_pipeline()

    print("--- Index is Ready! ---")

    # 2. Initialize LLM
    llm = LocalLLMInterface() # Assumes default connection

    # 3. Build the Chatbot Service
    service = ChatbotService(
        retrieval_engine=indexer,
        llm_interface=llm
    )

    # 4. Store *both* components in the app's state
    app.state.indexer = indexer
    app.state.chatbot_service = service

    print("--- SKB API Service is online. 'If we gonna die we die hard.' --- 🚀")

    yield

    # Code after 'yield' runs on shutdown
    print("--- SKB API Service is shutting down. ---")

# --- 3. Create the FastAPI App ---
app = FastAPI(
    title="Rouge Coders - Searchable Knowledge Base (SKB) API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:1574",
        "http://localhost:3000",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)

app.mount("/pdfs", StaticFiles(directory=str(PDF_FOLDER)), name="pdfs")

# --- 4. Pydantic Models (API Request/Response schemas) ---

# FOR /search (Raw SKB Search)
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

# --- THIS IS THE FIX ---
class SearchResult(BaseModel):
    heading: str
    text: str
    distance: float
    file_name: str     
    page_number: int   

class SearchResponse(BaseModel):
    results: List[SearchResult]

# FOR /query (Chatbot Search)
# FOR /query (Chatbot Search)
class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    reply: str
    sources: List[SearchResult] # <--- THIS IS THE FIX
    model: str = "unknown"
    backend: str = "unknown"

# FOR /upload and /rebuild-index (Management)
class UploadResponse(BaseModel):
    filename: str
    message: str
class RebuildResponse(BaseModel):
    status: str
    chunks_indexed: int
    message: str

# --- 5. Dependencies (How endpoints get the loaded models) ---

def get_indexer(request: Request) -> FAISSIndexer:
    return request.app.state.indexer

def get_chatbot_service(request: Request) -> ChatbotService:
    return request.app.state.chatbot_service

# --- 6. API Endpoints ---

@app.get("/")
def get_root():
    return {"message": "Rouge Coders SKB API is online."}

# ---
# Endpoint 1: The Core SKB Function
# ---
@app.post("/search", response_model=SearchResponse)
def post_raw_search(
        request: SearchRequest,
        indexer: FAISSIndexer = Depends(get_indexer)
):
    """
    Performs a raw vector search directly against the knowledge base
    and returns the source chunks without LLM-based reasoning.
    """
    try:
        results = indexer.search(query=request.query, top_k=request.top_k)
        print(results)
        return SearchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# ---
# Endpoint 2: The Supplementary Chatbot
# ---
@app.post("/query", response_model=ChatResponse)
def post_chatbot_query(
        request: ChatRequest,
        service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Processes a query using the full RAG pipeline (Retrieve, Rank, Reason)
    to generate a natural language answer.
    """
    try:
        response_data = service.handle_query(
            query=request.query,
            session_id=request.session_id
        )

        if "Error" in response_data.get("reply", ""):
            raise HTTPException(status_code=500, detail=response_data["reply"])

        return ChatResponse(
            reply=response_data.get("reply", "No reply generated."),
            sources=response_data.get("sources", []),
            model=response_data.get("model", "unknown"),
            backend=response_data.get("backend", "unknown")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
# ---
# Endpoint 3 & 4: Management API
# ---
@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Uploads a new PDF document to the data folder.
    This file will NOT be in the index until /rebuild-index is called.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")

    try:
        # Ensure the PDF folder exists
        os.makedirs(PDF_FOLDER, exist_ok=True)

        file_path = os.path.join(PDF_FOLDER, file.filename)

        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return UploadResponse(
            filename=file.filename,
            message="File uploaded successfully. Call /rebuild-index to add it to the KB."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

# We use BackgroundTasks to avoid a 5-minute timeout on the request
def _run_rebuild(app_state: dict):
    """Helper function to run the rebuild and update the app state."""
    new_indexer, chunks_indexed = _build_index_pipeline()

    # Atomically replace the old indexer and service
    app_state["indexer"] = new_indexer
    app_state["chatbot_service"].retrieval_engine = new_indexer
    print(f"--- Index successfully replaced in app state. {chunks_indexed} chunks active. ---")

@app.post("/rebuild-index", response_model=RebuildResponse)
def post_rebuild_index(
        background_tasks: BackgroundTasks,
        request: Request
):
    """
    Triggers a full rebuild of the FAISS index from all PDFs
    in the data folder. This is a long-running background task.
    """
    print("Rebuild request received. Starting task in background...")

    # Run the _run_rebuild function in the background
    background_tasks.add_task(_run_rebuild, request.app.state)

    return RebuildResponse(
        status="success",
        chunks_indexed=0, # This is async, so we can't know the count yet
        message="Index rebuild started in the background. "
                "This may take several minutes."
    )