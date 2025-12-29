"""
FAISS Index Adapter
-------------------
A configurable, enterprise-ready wrapper around FAISS that supports
dynamic index selection, easy persistence, and metadata mapping.

Designed for integration into SKB’s vector search pipeline.
"""

import faiss
import numpy as np
import os
from typing import List, Dict, Any, Optional


class FAISSIndexAdapter:
    """
    A flexible wrapper around FAISS indexes.
    
    Supports multiple index types (Flat, IVF, IVFPQ, HNSW)
    and optional GPU acceleration.
    """

    def __init__(self, dim: int, config: Dict[str, Any]):
        """
        Initialize the FAISS adapter.

        Args:
            dim (int): Dimension of embeddings.
            config (dict): Configuration options, e.g.:
                {
                    "index_type": "ivfpq",
                    "nlist": 100,
                    "m": 8,
                    "use_gpu": False,
                    "metric": "L2"
                }
        """
        self.dim = dim
        self.config = config
        self.index = None
        self.id_to_metadata = []
        self.metric = faiss.METRIC_INNER_PRODUCT if config.get("metric") == "IP" else faiss.METRIC_L2
        if "load_path" in config and os.path.exists(config["load_path"]):
            self.load(config["load_path"])
        else:
            self._build_index()

    def _build_index(self):
        index_type = self.config.get("index_type", "flat").lower()
        nlist = self.config.get("nlist", 100)
        m = self.config.get("m", 8)
        use_gpu = self.config.get("use_gpu", False)

        if index_type == "flat":
            self.index = faiss.IndexFlatL2(self.dim) if self.metric == faiss.METRIC_L2 else faiss.IndexFlatIP(self.dim)
        elif index_type == "ivf":
            quantizer = faiss.IndexFlatL2(self.dim)
            self.index = faiss.IndexIVFFlat(quantizer, self.dim, nlist, self.metric)
        elif index_type == "ivfpq":
            quantizer = faiss.IndexFlatL2(self.dim)
            self.index = faiss.IndexIVFPQ(quantizer, self.dim, nlist, m, 8)
        elif index_type == "hnsw":
            self.index = faiss.IndexHNSWFlat(self.dim, m)
        else:
            raise ValueError(f"Unknown index type: {index_type}")

        if use_gpu:
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)


    def add_embeddings(self, embeddings: np.ndarray, metadata: Optional[List[Dict[str, Any]]] = None):
        """
        Add embeddings and associated metadata to the index.
        """
        if self.metric == faiss.METRIC_INNER_PRODUCT:
            faiss.normalize_L2(embeddings)
        if not self.index.is_trained and hasattr(self.index, "train"):
            self.index.train(embeddings)
        self.index.add(embeddings)
        if metadata:
            self.id_to_metadata.extend(metadata)

    def search(self, query: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the index for the nearest neighbors.
        """
        if self.index.ntotal == 0:
            return []
    
        # normalize query for inner product metric
        if self.metric == faiss.METRIC_INNER_PRODUCT:
            faiss.normalize_L2(query)
    
        if query.ndim == 1:
            query = query[np.newaxis, :]
    
        distances, indices = self.index.search(query, k)
        results = []
    
        for i, idx_list in enumerate(indices):
            for j, idx in enumerate(idx_list):
                if idx < 0 or idx >= len(self.id_to_metadata):
                    meta = {}
                else:
                    meta = self.id_to_metadata[idx]
                results.append({
                    "distance": float(distances[i][j]),
                    "metadata": meta
                })
    
        return results
        
    def save(self, path: str):
        """
        Save the FAISS index to disk.
        """
        faiss.write_index(self.index, path)

        meta_path = path + ".meta"
        np.save(meta_path, np.array(self.id_to_metadata, dtype=object))

    def load(self, path: str):
        """
        Load the FAISS index and metadata.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Index not found: {path}")
        self.index = faiss.read_index(path)
        meta_path = path + ".meta.npy"
        if os.path.exists(meta_path):
            self.id_to_metadata = list(np.load(meta_path, allow_pickle=True))


    def info(self) -> Dict[str, Any]:
        """
        Return basic information about the current index.
        """
        return {
            "ntotal": self.index.ntotal if self.index else 0,
            "index_type": self.config.get("index_type"),
            "use_gpu": self.config.get("use_gpu"),
            "metric": self.config.get("metric"),
        }
