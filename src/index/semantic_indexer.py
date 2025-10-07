import os
import pickle
from pathlib import Path
import faiss
from src.models.embedder import Embedder
from src.extract.extract_text import extract_text


class SemanticIndexer:
    """
    Builds and manages a FAISS-based semantic index for PDFs.
    """

    def __init__(self, index_dir="semantic_index"):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        self.index_path = os.path.join(index_dir, "faiss.index")
        self.meta_path = os.path.join(index_dir, "metadata.pkl")

        self.embedder = Embedder()
        self.index = None
        self.metadata = []

        # load if exists
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.load_index()

    def load_index(self):
        print("[FAISS] Loading existing semantic index...")
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"[FAISS] Loaded {len(self.metadata)} documents.")

    def save_index(self):
        print("[FAISS] Saving semantic index...")
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)
        print("[FAISS] Index saved successfully.")

    def build_index(self, pdf_paths):
        """
        Create embeddings for PDFs and build FAISS index.
        """
        texts = []
        paths = []

        for pdf_path in pdf_paths:
            try:
                text = extract_text(pdf_path)
                if not text.strip():
                    print(f"[WARN] Empty text for {pdf_path}")
                    continue
                texts.append(text)
                paths.append(pdf_path)
            except Exception as e:
                print(f"[ERROR] Failed to extract {pdf_path}: {e}")

        print(f"[INFO] Generating embeddings for {len(texts)} PDFs...")
        embeddings = self.embedder.encode(texts)
        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)
        self.metadata = paths

        self.save_index()
        print(f"[DONE] Indexed {len(paths)} PDFs semantically.")

    def add_document(self, pdf_path):
        """
        Add a single PDF to the existing semantic index.
        """
        text = extract_text(pdf_path)
        emb = self.embedder.encode(text)
        if self.index is None:
            self.index = faiss.IndexFlatIP(emb.shape[1])
        self.index.add(emb)
        self.metadata.append(pdf_path)
        self.save_index()
        print(f"[ADDED] {pdf_path}")

    def add_documents_batch(self, data_dir="data"):
        """
        Recursively add all PDFs under `data_dir` to the existing semantic index.
        """
        pdf_files = list(Path(data_dir).rglob("*.pdf"))
        if not pdf_files:
            print(f"[WARN] No PDF files found under '{data_dir}'")
            return

        print(f"[INFO] Adding {len(pdf_files)} PDFs to existing semantic index...")
        for pdf_path in pdf_files:
            try:
                self.add_document(str(pdf_path))
            except Exception as e:
                print(f"[ERROR] Failed to add {pdf_path}: {e}")
        print(f"[DONE] Batch addition complete.")
