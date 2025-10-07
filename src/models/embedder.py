from sentence_transformers import SentenceTransformer
import numpy as np


class Embedder:
    """
    Wrapper around a sentence-transformer model for generating embeddings.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"[MODEL] Loading embedding model '{model_name}'...")
        self.model = SentenceTransformer(model_name)
        print("[MODEL] Model loaded successfully.")

    def encode(self, texts):
        """
        Encode one or more texts into embeddings.

        Args:
            texts (str | list[str]): Input text(s) to encode.

        Returns:
            np.ndarray: Embedding array (shape: [n, dim])
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True)
        return np.array(embeddings)
