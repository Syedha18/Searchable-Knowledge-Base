import numpy as np
from sentence_transformers import SentenceTransformer

model: SentenceTransformer | None = None

def set_global_embedder(embedder: SentenceTransformer):
    """Attach global SentenceTransformer model for reuse."""
    global model
    model = embedder


def get_embedding(text: str) -> np.ndarray:
    """Return normalized embedding for a single text."""
    if model is None:
        raise RuntimeError("Embedding model not initialized. Call set_global_embedder().")
    emb = model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    return emb[0]


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    return float(np.dot(vec1, vec2))

