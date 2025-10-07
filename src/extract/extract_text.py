import os
import tempfile
from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader


def extract_text(pdf_path: str, use_ocr_fallback: bool = True) -> str:
    """
    Extract text from a PDF file.

    - Uses PyPDF2 for digital PDFs.
    - Falls back to OCR (Tesseract) for scanned/image PDFs if enabled.

    Args:
        pdf_path (str): Path to the input PDF file.
        use_ocr_fallback (bool): If True, runs OCR when no text is found.

    Returns:
        str: Extracted text from the PDF.
    """
    text_content = []

    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            extracted = page.extract_text() or ""
            text_content.append(extracted)

        text = "\n".join(text_content).strip()

        # If no text found (likely a scanned PDF)
        if not text and use_ocr_fallback:
            print(f"[INFO] No text detected in {os.path.basename(pdf_path)} — using OCR fallback...")
            text = _extract_text_ocr(pdf_path)

        return text

    except Exception as e:
        print(f"[ERROR] Failed to extract text from {pdf_path}: {e}")
        if use_ocr_fallback:
            return _extract_text_ocr(pdf_path)
        return ""


def _extract_text_ocr(pdf_path: str) -> str:
    """
    Perform OCR extraction on a scanned PDF.
    """
    ocr_text = []
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            images = convert_from_path(pdf_path, output_folder=temp_dir, fmt='jpeg')
            for i, img in enumerate(images):
                text = pytesseract.image_to_string(img)
                ocr_text.append(text)
                print(f"[OCR] Processed page {i + 1}/{len(images)}")
        except Exception as e:
            print(f"[ERROR] OCR failed: {e}")
    return "\n".join(ocr_text).strip()
