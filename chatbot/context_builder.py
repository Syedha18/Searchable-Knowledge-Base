# chatbot/context_builder.py
from typing import List, Dict, Optional
import textwrap

class ContextBuilder:
    """
    Builds a reasoning-ready prompt from retrieved chunks and chat history.
    """

    def __init__(self, max_context_tokens: int = 4000):
        self.max_context_tokens = max_context_tokens

    def _format_chunk(self, chunk: Dict[str, str], index: int) -> str:
        """
        Format a retrieved chunk with metadata.
        """
        content = chunk.get("text", "").strip()
        source = chunk.get("source", "unknown")
        return f"[{index}] (Source: {source})\n{content}"

    def build_prompt(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, str]],
        chat_history: Optional[List[Dict[str, str]]] = None,
        style: str = "reasoning",
    ) -> Dict[str, str]:
        """
        Build the full LLM prompt for reasoning.

        Args:
            query: User's query text.
            retrieved_chunks: List of dicts: {text, source, metadata?}.
            chat_history: Optional list of previous turns [{'user':..., 'bot':...}]
            style: Prompting style ('reasoning', 'summary', etc.)

        Returns:
            Dict with {'prompt': str, 'sources': List[str]}
        """
        # --- Format retrieved context ---
        formatted_chunks = [
            self._format_chunk(chunk, i + 1)
            for i, chunk in enumerate(retrieved_chunks)
        ]
        sources = [chunk.get("source", "unknown") for chunk in retrieved_chunks]

        # --- Compile chat history ---
        history_text = ""
        if chat_history:
            for turn in chat_history[-3:]:  # keep last 3 for brevity
                history_text += f"User: {turn['user']}\nAssistant: {turn['bot']}\n"

        # --- Build reasoning template ---
        system_prompt = textwrap.dedent(f"""
        You are a domain expert assistant. Use the given context to reason and answer accurately.

        Context:
        {chr(10).join(formatted_chunks)}

        Chat History (if relevant):
        {history_text.strip()}

        Task:
        - Answer the user's question based strictly on the context.
        - If unsure, state that the information is not available.
        - Provide logical reasoning before the conclusion.

        User Question:
        {query}
        """)

        return {"prompt": system_prompt.strip(), "sources": sources}
