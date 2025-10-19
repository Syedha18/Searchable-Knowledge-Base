# api/chatbot_api.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import uvicorn


# Import your modules
from retrieval.retrieval_engine import RetrievalEngine
from context_builder import ContextBuilder
from llm_interface import LocalLLMInterface
from chatbot_service import ChatbotService

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(
    title="SKB Reasoning Chatbot API",
    description="Local reasoning chatbot over enterprise knowledge base.",
    version="1.0.0",
)

# -----------------------------
# Pydantic Models
# -----------------------------
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    reply: str
    sources: list
    model: str
    backend: str

# -----------------------------
# Initialize components
# -----------------------------
retriever = RetrievalEngine(index_path="data/faiss_index", db_uri="mongodb://localhost:27017/skb")
llm = LocalLLMInterface(model="llama3:instruct", backend="ollama")
context_builder = ContextBuilder()
chatbot_service = ChatbotService(retriever, llm, context_builder)

# -----------------------------
# API Endpoints
# -----------------------------
@app.post("/api/chat/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process a user query and return reasoning response + sources.
    """
    try:
        response = chatbot_service.handle_query(query=request.query, session_id=request.session_id)
        if "reply" not in response:
            raise HTTPException(status_code=500, detail="Chatbot failed to generate a response.")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# Optional: root health check
# -----------------------------
@app.get("/")
async def root():
    return {"message": "SKB Chatbot API is running!"}


# -----------------------------
# Run server (if executed directly)
# -----------------------------
if __name__ == "_main_":
    uvicorn.run("api.chatbot_api:app", host="0.0.0.0", port=8000, reload=True)
