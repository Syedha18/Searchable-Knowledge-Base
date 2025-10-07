from pathlib import Path
from src.index.semantic_indexer import SemanticIndexer

# Recursively find all PDFs in the 'data' folder and convert to strings
pdfs = [str(p) for p in Path("../../data").rglob("*.pdf")]

print(f"Found {len(pdfs)} PDFs")  # sanity check

# Initialize the semantic indexer
indexer = SemanticIndexer(index_dir="semantic_index")

# Build the semantic index
indexer.build_index(pdfs)
