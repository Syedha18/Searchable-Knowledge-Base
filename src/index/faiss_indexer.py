import faiss
from typing import List, Dict
from sentence_transformers import SentenceTransformer

class FAISSIndexer:
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(embedding_model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dim)
        self.metadata = []

    def add_chunks(self, chunks: List[Dict]):
        """
        chunks: List of semantic chunks, each dict must have:
            'heading': str
            'text': str
        """
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        self.index.add(embeddings)
        self.metadata.extend(chunks)

    def search(self, query: str, top_k: int = 5):
        """
        Returns top_k similar chunks for the query.
        """
        query_emb = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_emb, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                results.append({
                    "heading": self.metadata[idx]["heading"],
                    "text": self.metadata[idx]["text"],
                    "distance": float(dist)
                })
        return results
