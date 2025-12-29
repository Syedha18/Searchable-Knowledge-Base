from src.utils.pdf_extractor import PDFExtractor
from src.index.faiss_index_adapter import FAISSIndexAdapter
import numpy as np
from sentence_transformers import SentenceTransformer

pdf_folder = "src/data/sample_pdfs"   
extractor = PDFExtractor()
semantic_chunks, positional_chunks = extractor.extract_from_folder(pdf_folder)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def embedding(texts):
    # Can handle a single string or list of strings
    if isinstance(texts, str):
        texts = [texts]
    return np.array(embedding_model.encode(texts, convert_to_numpy=True, normalize_embeddings=True))


embedding_dim = 384
embeddings = np.vstack([embedding(c["text"]) for c in semantic_chunks])
metadata = [{"heading": c["heading"], "text": c["text"]} for c in semantic_chunks]

faiss_config = {
    "index_type": "ivfpq",
    "nlist": 100,
    "m": 8,
    "use_gpu": False,
    "metric": "L2",
}
faiss_adapter = FAISSIndexAdapter(dim=embedding_dim, config=faiss_config)
faiss_adapter.add_embeddings(embeddings, metadata)
faiss_adapter.save("faiss_test.index")

# --- 4. Search ---
query_text = "annual reports"
query_embedding = embedding(query_text)
results = faiss_adapter.search(query_embedding, k=5)

# --- 5. Print results ---
for r in results:
    print(f"Distance: {r['distance']:.4f} | Heading: {r['metadata'].get('heading')} | Snippet: {r['metadata'].get('text')[:100]}...")
