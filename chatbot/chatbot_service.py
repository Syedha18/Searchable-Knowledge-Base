# chatbot/chatbot_service.py
from typing import List, Dict, Optional, Generator

from src.index.faiss_indexer import FAISSIndexer  
from chatbot.context_builder import ContextBuilder
from chatbot.llm_interface import LocalLLMInterface


class ChatbotService:
    """
    Main reasoning chatbot orchestrator for SKB.
    """

    def __init__(
        self,
        retrieval_engine: FAISSIndexer,
        llm_interface: LocalLLMInterface,
        context_builder: Optional[ContextBuilder] = None,
    ):
        self.retrieval_engine = retrieval_engine
        self.llm_interface = llm_interface
        self.context_builder = context_builder or ContextBuilder()

        # In-memory simple session storage (extendable to Redis later)
        self.sessions: Dict[str, List[Dict[str, str]]] = {}

    # -------------------------------------------------
    # Session Management
    # -------------------------------------------------
    def _get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.sessions.get(session_id, [])

    def _update_history(self, session_id: str, user_msg: str, bot_reply: str):
        history = self.sessions.setdefault(session_id, [])
        history.append({"user": user_msg, "bot": bot_reply})
        # Keep last 5 exchanges for brevity
        self.sessions[session_id] = history[-5:]

    def handle_query_stream(self, query: str, session_id: str = "default") -> Generator[Dict[str, any], None, None]:

        try:
            # --- Step 1: Retrieve ---
            retrieved_chunks = self.retrieval_engine.search(query, top_k=5)
            if not retrieved_chunks:
                # Yield final error/metadata immediately
                yield {
                    "reply": "No relevant information found in the knowledge base.",
                    "sources": [],
                    "event": "end",
                }
                return
    
            # --- Step 2: Build Context ---
            chat_history = self._get_history(session_id)
            prompt_data = self.context_builder.build_prompt(
                query=query,
                retrieved_chunks=retrieved_chunks,
                chat_history=chat_history,
                style="reasoning",
            )
    
            # --- Step 3: Yield Initial Metadata (Sources) ---
            # The frontend needs this info before the stream starts.
            yield {
                "sources": retrieved_chunks,
                "model": self.llm_interface.model,
                "backend": self.llm_interface.backend,
                "event": "start",
            }
    
            # --- Step 4: Generate and Stream Response ---
            full_reply_text = ""
    
            # 🔑 Use the streaming function here!
            for chunk in self.llm_interface.stream_response(prompt_data["prompt"]):
                full_reply_text += chunk
    
                # Yield the text chunk immediately as a simple dictionary
                yield {
                    "reply_chunk": chunk,
                    "event": "stream",
                }
    
            # --- Step 5: Update Session & Finalize ---
            self._update_history(session_id, query, full_reply_text)
    
            # Yield a final signal to the frontend
            yield {"event": "end"}
    
        except Exception as e:
            yield {
                "reply": f"⚠ Error: Internal Server Error: {str(e)}",
                "sources": [],
                "event": "error",
            }
