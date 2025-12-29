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
import json

from src.utils.pdf_processor import PDFProcessor
from src.utils.image_captioner import ImageCaptioner
from chatbot.chatbot_service import ChatbotService
from src.index.faiss_indexer import FAISSIndexer
from chatbot.llm_interface import LocalLLMInterface
from src.utils.pdf_extractor import PDFExtractor
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from src.config.settings import (
    PDF_FOLDER, INDEX_FILE, EMBEDDING_MODEL, FAISS_CONFIG, VISUAL_DATA_DIR
)
from src.utils.embedder import set_global_embedder, get_embedding, cosine_similarity
from src.config.settings import USE_MONGODB
from src.repositories.visual_repository import (
    insert_visual_elements,
    delete_by_pdf
)
from datetime import datetime
from src.utils.build_visual_doc import build_visual_documents
from src.repositories.visual_repository import get_visuals_by_pdfs

def build_text_index_pipeline() -> (FAISSIndexer, int):
    """
    Extracts text from PDFs, embeds it, and loads it into the FAISS index.
    Returns a newly built and saved indexer and chunk count.
    """
    print("--- Text Index Rebuild Initiated ---")
    start_time = time.time()

    indexer = FAISSIndexer(
        embedding_model_name=EMBEDDING_MODEL,
        index_config=FAISS_CONFIG
    )

    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        print(f"Created PDF folder: {PDF_FOLDER}")
        return indexer, 0

    extractor = PDFExtractor()
    semantic_chunks, _ = extractor.extract_from_folder(PDF_FOLDER)
    print(f"Found {len(semantic_chunks)} semantic chunks.")

    if semantic_chunks:
        indexer.add_chunks(semantic_chunks)
        print(f"Saving index to {INDEX_FILE}...")
        os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
        indexer.save(INDEX_FILE)

    total_time = time.time() - start_time
    print(f"--- Text index build complete in {total_time:.2f}s ---")
    return indexer, len(semantic_chunks)

async def build_visual_index_pipeline():
    """
    Processes PDFs for images and tables, generates captions,
    and stores visual metadata (MongoDB or JSON fallback).
    """
    print("--- Visual Data Processing Initiated ---")
    start_time = time.time()
    captioner = ImageCaptioner()

    if not os.path.exists(PDF_FOLDER):
        print("No PDFs found for visual processing.")
        return

    for pdf_file in os.listdir(PDF_FOLDER):
        if not pdf_file.lower().endswith(".pdf"):
            continue

        pdf_path = PDF_FOLDER / pdf_file
        pdf_output_dir = VISUAL_DATA_DIR / pdf_file.replace(".pdf", "")
        processor = PDFProcessor(str(pdf_path), output_dir=str(pdf_output_dir))
        results = processor.process_all()

        # Generate captions for extracted images
        image_paths = [img["path"] for img in results.get("images", [])]
        if image_paths:
            captions = captioner.generate_captions_batch(image_paths)
            for i, img_data in enumerate(results["images"]):
                img_data["caption"] = captions[i]["caption"]

        pdf_name = pdf_file.replace(".pdf", "")

        if USE_MONGODB:
            docs = build_visual_documents(pdf_name, results)
            await delete_by_pdf(pdf_name)
            await insert_visual_elements(docs)
            print(f"[MongoDB] Visual data for {pdf_file} stored successfully")
        else:
            os.makedirs(VISUAL_DATA_DIR, exist_ok=True)
            results_path = VISUAL_DATA_DIR / f"{pdf_file}_results.json"
            with open(results_path, "w") as f:
                json.dump(results, f, indent=2)
            print(f"[JSON] Visual data for {pdf_file} saved at {results_path}")

    total_time = time.time() - start_time
    print(f"--- Visual data processing complete in {total_time:.2f}s ---")
    
def dedup_text_results(results):
    """
    Deduplicate FAISS text results by (file_name, page_number, heading).
    Keeps the chunk with the lowest distance (best match).
    """
    deduped = {}

    for r in results:
        key = (
            r.get("file_name"),
            r.get("page_number"),
            r.get("heading"),
        )

        # Keep the best (lowest distance) chunk per section
        if key not in deduped or r["distance"] < deduped[key]["distance"]:
            deduped[key] = r

    return list(deduped.values())


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- API Boot Phase ---")

    if os.path.exists(INDEX_FILE):
        try:
            print(f"Loading existing index from {INDEX_FILE}...")
            indexer = FAISSIndexer(embedding_model_name=EMBEDDING_MODEL, index_config=FAISS_CONFIG)
            indexer.load(INDEX_FILE)
            print("Text index loaded successfully.")
        except Exception as e:
            print(f"Error loading index: {e}. Rebuilding text index...")
            indexer, _ = build_text_index_pipeline()
    else:
        print("No text index found. Building new text index...")
        indexer, _ = build_text_index_pipeline()

    print("--- Text Index Ready ---")

    print("--- Checking visual data... ---")
    try:
        if not VISUAL_DATA_DIR.exists() or not any(VISUAL_DATA_DIR.iterdir()):
            print("--- Visual data missing. Processing all PDFs... ---")
            await build_visual_index_pipeline()  
        else:
            print("--- Visual data already exists. Skipping visual processing. ---")
    except Exception as e:
        print(f"[WARN] Visual index build failed: {e}. Starting in text-only mode.")


    set_global_embedder(indexer.model)

    llm = LocalLLMInterface()

    service = ChatbotService(
        retrieval_engine=indexer,
        llm_interface=llm
    )

    app.state.indexer = indexer
    app.state.chatbot_service = service

    print("--- SKB API Service is online. ---")

    yield

    print("--- SKB API Service is shutting down. ---")

app = FastAPI(
    title="Searchable Knowledge Base (SKB) API",
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
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.mount("/pdfs", StaticFiles(directory=str(PDF_FOLDER)), name="pdfs")
app.mount("/visuals", StaticFiles(directory=str(VISUAL_DATA_DIR)), name="visuals")


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    
class SearchResult(BaseModel):
    heading: str
    text: str
    distance: float
    file_name: str     
    page_number: int

class VisualItem(BaseModel):
    filename: str
    page: int
    type: str  # "image" or "table"
    caption: str | None = None
    rows: int | None = None
    columns: int | None = None
    url: str
    score: float | None = None


class SearchResponse(BaseModel):
    text_results: List[SearchResult]
    visual_results: List[VisualItem]

# FOR /query (Chatbot Search)
class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    reply: str
    sources: List[SearchResult]
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


def get_indexer(request: Request) -> FAISSIndexer:
    return request.app.state.indexer

def get_chatbot_service(request: Request) -> ChatbotService:
    return request.app.state.chatbot_service


@app.get("/")
def get_root():
    return {"message": "SKB API is online."}


@app.post("/search", response_model=SearchResponse)
async def post_unified_search(
        request: SearchRequest,
        indexer: FAISSIndexer = Depends(get_indexer)
):
    """
    Performs a unified vector search across both
    text chunks (FAISS) and visual data (captions/tables).
    """
    try:
        if not request.query.strip():
            return SearchResponse(text_results=[], visual_results=[])
            
        text_results = indexer.search(query=request.query, top_k=request.top_k)
        
        text_results = dedup_text_results(text_results)
        
        text_results = [SearchResult(**r) for r in text_results]

        # --- VISUAL SEARCH ---
        query_embedding = get_embedding(request.query)
        related_pdfs = {res.file_name.replace(".pdf", "") for res in text_results}
        
        visuals = []

        if USE_MONGODB:
            # --- MONGODB SEARCH ---
            visual_records = await get_visuals_by_pdfs(list(related_pdfs))
            
            for record in visual_records:
                # Map MongoDB record to visual item structure
                item_type = record.get("type")
                
                if item_type == "image":
                    caption = record.get("caption", "")
                    if caption:
                        score = cosine_similarity(query_embedding, get_embedding(caption))
                        if score > 0.10:
                            visuals.append({
                                "filename": record["filename"],
                                "page": record["page_number"],
                                "type": "image",
                                "caption": caption,
                                "url": f"/visuals/{record['pdf_name']}/images/{record['filename']}",
                                "score": score,
                            })
                            
                elif item_type == "table":
                    # Build description for table
                    meta = record.get("table_metadata", {})
                    rows = meta.get("rows")
                    cols = meta.get("columns")
                    desc = f"Table with {rows} rows and {cols} columns."
                    
                    score = cosine_similarity(query_embedding, get_embedding(desc))
                    if score > 0.99:
                        visuals.append({
                            "filename": record["filename"],
                            "page": record["page_number"],
                            "type": "table",
                            "rows": rows,
                            "columns": cols,
                            "url": f"/visuals/{record['pdf_name']}/tables/{record['filename']}",
                            "score": score,
                        })

        else:
            # --- FILE SYSTEM SEARCH (LEGACY) ---
            for pdf_name in related_pdfs:
                result_json_path = os.path.join(VISUAL_DATA_DIR, f"{pdf_name}.pdf_results.json")

                if not os.path.exists(result_json_path):
                    continue
                
                with open(result_json_path, "r") as f:
                    visual_data = json.load(f)

                # Search through image captions
                for img in visual_data.get("images", []):
                    caption = img.get("caption", "")
                    if caption:
                        score = cosine_similarity(query_embedding, get_embedding(caption))
                        if score > 0.10:
                            visuals.append({
                                "filename": img["filename"],
                                "page": img["page"],
                                "type": "image",
                                "caption": caption,
                                "url": f"/visuals/{pdf_name}/images/{img['filename']}",
                                "score": score,
                            })

                # Search through tables
                for tbl in visual_data.get("tables", []):
                    desc = f"Table with {tbl['rows']} rows and {tbl['columns']} columns."
                    score = cosine_similarity(query_embedding, get_embedding(desc))
                    if score > 0.99:
                        visuals.append({
                            "filename": tbl["filename"],
                            "page": tbl["page"],
                            "type": "table",
                            "rows": tbl.get("rows"),
                            "columns": tbl.get("columns"),
                            "url": f"/visuals/{pdf_name}/tables/{tbl['filename']}",
                            "score": score,
                        })

        visuals.sort(key=lambda v: v["score"], reverse=True)

        return SearchResponse(
            text_results=text_results,
            visual_results=visuals[:request.top_k]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unified search failed: {str(e)}")


@app.post("/stream_query")
def stream_chatbot_query(
        request: ChatRequest,
        service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Processes a query and streams the response chunks back to the client.
    """
    try:
        def stream_generator():

            for response_data in service.handle_query_stream(
                    query=request.query,
                    session_id=request.session_id
            ):
                # FastAPI requires bytes/strings for streaming. We use JSONL format.
                yield json.dumps(response_data) + "\n"

        return StreamingResponse(
            stream_generator(),
            media_type="application/json"
        )

    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Failed to start stream: {str(e)}")

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

async def _run_rebuild(app_state: dict, rebuild_visuals: bool = False):
    """
    Helper function to rebuild the text index and optionally visual data,
    then update the app state atomically.
    """
    print("--- Rebuild task started ---")

    # Rebuild text index
    new_indexer, chunks_indexed = build_text_index_pipeline()

    # Rebuild visual data only if requested
    if rebuild_visuals:
        print("--- Rebuilding missing visual data ---")
        await build_visual_index_pipeline()
    else:
        print("--- Skipping visual data rebuild ---")

    # Atomically replace the old indexer in app state
    app_state["indexer"] = new_indexer
    app_state["chatbot_service"].retrieval_engine = new_indexer

    print(f"--- Rebuild complete: {chunks_indexed} text chunks indexed ---")


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