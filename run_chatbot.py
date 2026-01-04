# run_chatbot.py
import os
import time
from chatbot.chatbot_service import ChatbotService
from src.index.faiss_indexer import FAISSIndexer 
from chatbot.llm_interface import LocalLLMInterface
from src.utils.pdf_extractor import PDFExtractor

# --- Config ---
# Imported from centralized settings to ensure DRY principle
from src.config.settings import (
    PDF_FOLDER,
    INDEX_FILE,
    EMBEDDING_MODEL,
    FAISS_CONFIG
)

# --- 1. Initialize the Indexer ---
# This just loads the embedding model, not the data
indexer = FAISSIndexer(
    embedding_model_name=EMBEDDING_MODEL,
    index_config=FAISS_CONFIG
)

# --- 2. Build or Load the Index ---
if os.path.exists(INDEX_FILE):
    try:
        print(f"Loading existing index from {INDEX_FILE}...")
        start_time = time.time()
        indexer.load(INDEX_FILE)
        print(f"Index loaded in {time.time() - start_time:.2f}s")
    except Exception as e:
        print(f"Error loading index: {e}. Re-building...")
        os.remove(INDEX_FILE) # Remove corrupted file
        # Fall through to the 'else' block

if not os.path.exists(INDEX_FILE):
    print("--- Index Build Phase ---")
    start_time = time.time()

    # 1. Extract
    print(f"Extracting data from {PDF_FOLDER}...")
    extractor = PDFExtractor()
    semantic_chunks, _ = extractor.extract_from_folder(PDF_FOLDER)
    print(f"Found {len(semantic_chunks)} semantic chunks.")

    # 2. Add and Train
    if semantic_chunks:
        indexer.add_chunks(semantic_chunks)

        # 3. Save
        print(f"Saving index to {INDEX_FILE}...")
        # Ensure the 'storage' directory exists
        os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
        indexer.save(INDEX_FILE)
        print(f"Index built and saved in {time.time() - start_time:.2f}s")
    else:
        print("No chunks found. Index is empty.")

print("--- Index is Ready! ---")


# --- 3. Initialize and Run the Chatbot ---
print("\n--- Chatbot Service Phase ---")

# Initialize other components
llm = LocalLLMInterface() # Assumes default connection to Ollama

# Initialize the Chatbot Service
# We pass it the *loaded* and ready indexer
chatbot = ChatbotService(
    retrieval_engine=indexer,
    llm_interface=llm
)
print("Chatbot service is online. 🚀")

# --- 4. Run your query ---
query_text = "annual reports"
print(f"\n--- Querying Chatbot ---")
print(f"USER: {query_text}")

response = chatbot.handle_query(query_text, session_id="test_session")

print(f"\nBOT: {response['reply']}")
print("\n--- Sources Used ---")
if response['sources']:
    for source in response['sources']:
        print(source)
        print("---")
else:
    print("No sources were used for this reply.")