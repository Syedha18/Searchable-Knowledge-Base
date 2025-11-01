# chatbot/chatbot_service.py
from typing import List, Dict, Optional

from src.index.faiss_indexer import FAISSIndexer  # your FAISS+NoSQL layer
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

    # -------------------------------------------------
    # Core Interaction
    # -------------------------------------------------
    def handle_query(self, query: str, session_id: str = "default") -> Dict[str, any]:
        """
        Process a user query end-to-end:
        1. Retrieve relevant chunks
        2. Build reasoning prompt
        3. Generate LLM response
        4. Return response + sources
        """
        try:
            # --- Step 1: Retrieve ---
            retrieved_chunks = self.retrieval_engine.search(query, top_k=5)
            if not retrieved_chunks:
                return {
                    "reply": "No relevant information found in the knowledge base.",
                    "sources": [],
                }

            # --- Step 2: Build Context ---
            chat_history = self._get_history(session_id)
            prompt_data = self.context_builder.build_prompt(
                query=query,
                retrieved_chunks=retrieved_chunks,
                chat_history=chat_history,
                style="reasoning",
            )

            # --- Step 3: Generate Reasoning Response ---
            llm_output = self.llm_interface.generate_response(prompt_data["prompt"])
            bot_reply = llm_output["response"]

            # --- Step 4: Update Session ---
            self._update_history(session_id, query, bot_reply)

            return {
                "reply": bot_reply,
                "sources": retrieved_chunks,  
                "model": llm_output["model"],
                "backend": llm_output["backend"],
            }

        except Exception as e:
            return {
                "reply": f"⚠ Error: {str(e)}",
                "sources": [],
            }
