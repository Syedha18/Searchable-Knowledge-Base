# chatbot/llm_interface.py
import requests
from typing import Optional, Dict, Any, Generator
import json



class LocalLLMInterface:
    """
    Interface for running prompts on a local LLM (e.g., Ollama, vLLM, LM Studio).
    """

    def __init__(
        self,
        backend: str = "ollama",
        model: str = "llama3:instruct",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ):
        self.backend = backend.lower()
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens

        if self.backend not in ["ollama", "vllm"]:
            raise ValueError(f"Unsupported backend: {self.backend}")

    # ------------------------------------------
    # Ollama Inference
    # ------------------------------------------
    def _query_ollama(self, prompt: str) -> Generator[str, None, None]: # <-- CHANGED
        """
        Send prompt to Ollama REST API and stream the response.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "num_predict": self.max_tokens,
            "stream": True  # <--- THIS IS THE MAGIC!
        }

        # Note: stream=True on the request, and "stream": True in the payload
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()  # <-- Good practice: check for HTTP errors

        # No more response.json()! We loop over the stream.
        for line in response.iter_lines():
            if line:
                try:
                    # Each line is its own tiny JSON object
                    chunk = json.loads(line.decode('utf-8'))
                    
                    # Pull out the text piece
                    text_chunk = chunk.get('response', '')
                    if text_chunk:
                        yield text_chunk  # <-- We YIELD the piece instead of returning
                    
                    # Ollama sends a 'done' message at the end
                    if chunk.get('done', False):
                        break  # Stop the loop
                except  json.JSONDecodeError:
                    # Sometimes Ollama sends weird keep-alive lines, just ignore them
                    pass

    # ------------------------------------------
    # vLLM Inference (Optional)
    # ------------------------------------------
    def _query_vllm(self, prompt: str) -> str:
        """
        Send prompt to vLLM REST API (OpenAI-compatible).
        """
        url = f"{self.base_url}/v1/completions"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"vLLM request failed: {response.text}")

        data = response.json()
        return data["choices"][0]["text"].strip()

    # ------------------------------------------
    # Unified Entry Point
    # ------------------------------------------
# ------------------------------------------
    # Unified Entry Point
    # ------------------------------------------
    def generate_response(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a reasoning response using the configured backend.
        This function WAITS for the full response and returns it.
        """
        text_chunks = []
        # We loop over the generator and collect all the pieces
        for chunk in self.stream_response(prompt): # <-- We use our NEW function
            text_chunks.append(chunk)
        
        full_text = "".join(text_chunks)

        return {
            "model": self.model,
            "backend": self.backend,
            "response": full_text, # <-- Return the complete, joined text
        }
    
    # --- ADD THIS NEW FUNCTION ---
    def stream_response(self, prompt: str) -> Generator[str, None, None]:
        """
        Generate a response and stream the text chunks as they arrive.
        """
        if self.backend == "ollama":
            yield from self._query_ollama(prompt)
        elif self.backend == "vllm":
            yield from self._query_vllm(prompt)
        else:
            raise NotImplementedError(f"Backend '{self.backend}' not supported")
