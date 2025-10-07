import os
from pathlib import Path
from src.extract.extract_text import extract_text
from src.index.indexer import add_to_index
from src.eval.benchmark import measure_extraction_speed


def batch_index_all(data_dir="data", index_dir="indexdir"):
    """
    Recursively index all PDFs under `data_dir` (including subfolders).
    Uses OCR fallback for scanned PDFs and logs performance per file.
    """
    pdf_files = list(Path(data_dir).rglob("*.pdf"))
    if not pdf_files:
        print(f"[WARN] No PDF files found under '{data_dir}'")
        return

    print(f"[INFO] Found {len(pdf_files)} PDF(s) under '{data_dir}' — starting indexing...\n")
    total_pages = 0
    total_time = 0.0

    for pdf_path in pdf_files:
        pdf_path = str(pdf_path)
        try:
            text, duration, pages_per_sec = measure_extraction_speed(extract_text, pdf_path)
            add_to_index(pdf_path, text, index_dir)
            total_time += duration
            total_pages += pages_per_sec * duration  # reconstruct total pages
            print(f"  ↳ Indexed {os.path.basename(pdf_path)} at {pages_per_sec:.2f} pages/sec\n")
        except Exception as e:
            print(f"[ERROR] Failed to index {pdf_path}: {e}\n")

    print("=" * 60)
    if total_time > 0:
        avg_speed = total_pages / total_time
        print(f"[SUMMARY] Indexed {len(pdf_files)} PDFs in {total_time:.2f}s "
              f"at avg {avg_speed:.2f} pages/sec")
    else:
        print("[SUMMARY] No PDFs indexed successfully.")
    print("=" * 60)
