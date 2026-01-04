# chatbot/context_builder.py
from typing import List, Dict, Optional
from src.schemas.search import SearchResult
import textwrap

class ContextBuilder:
    """
    Builds a reasoning-ready prompt from retrieved chunks and chat history.
    """

    def __init__(self, max_context_tokens: int = 4000):
        self.max_context_tokens = max_context_tokens

    def _format_chunk(self, chunk: SearchResult, index: int) -> str:
        """
        Format a retrieved chunk with metadata.
        """
        content = chunk.text.strip()
        source = chunk.file_name
        return f"[{index}] (Source: {source})\n{content}"

    def build_prompt(
        self,
        query: str,
        retrieved_chunks: List[SearchResult],
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
        sources = [chunk.file_name for chunk in retrieved_chunks]

        # --- Compile chat history ---
        history_text = ""
        if chat_history:
            for turn in chat_history[-3:]:  # keep last 3 for brevity
                history_text += f"User: {turn['user']}\nAssistant: {turn['bot']}\n"

        # --- Build reasoning template ---
        system_prompt = textwrap.dedent(f"""
        You are a knowledgeable and helpful assistant.
        
        Use the retrieved context when it is relevant to answer the user's question accurately.
        If the context does not fully answer the question, say so clearly and respond at a high level without guessing details.
        
        Context:
        {chr(10).join(formatted_chunks)}
        
        Recent Chat History (if relevant):
        {history_text.strip()}
        
        Response Guidelines:
        - For greetings or casual conversation, reply naturally and warmly.
        - For information-seeking questions, ground your answer in the provided context when applicable.
        - Show reasoning only when it improves clarity.
        - Do not invent facts that are not supported by the context.
        
        User Question:
        {query}
        """)

        return {"prompt": system_prompt.strip(), "sources": sources}
