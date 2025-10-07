import time
from typing import Callable, Any, Tuple


def measure_extraction_speed(
        extractor_func: Callable[[str], Any],
        pdf_path: str
) -> Tuple[Any, float, float]:
    """
    Measure speed of a text extraction function.

    Args:
        extractor_func (callable): Function that extracts text from a PDF path.
        pdf_path (str): Path to the PDF file.

    Returns:
        (result, duration, pages_per_second)
    """
    from PyPDF2 import PdfReader
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
    except Exception:
        total_pages = 1  # fallback for OCR-only PDFs

    start = time.time()
    result = extractor_func(pdf_path)
    duration = time.time() - start
    pages_per_sec = total_pages / duration if duration > 0 else 0

    print(f"[BENCHMARK] {pdf_path}: {total_pages} pages in {duration:.2f}s ({pages_per_sec:.2f} pages/sec)")
    return result, duration, pages_per_sec
