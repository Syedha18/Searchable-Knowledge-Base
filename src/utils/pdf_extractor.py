import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pathlib import Path
from typing import List, Dict, Tuple
import re

class PDFExtractor:
    """
    Extract semantic and positional chunks from digital and scanned PDFs.
    """

    def __init__(self):
        # Threshold multiplier for heading detection
        self.heading_font_multiplier = 1.3
        # Optional: keywords that are likely headings
        self.heading_keywords = [
            "introduction", "overview", "summary", "policy", "scope",
            "purpose", "objectives", "responsibilities", "safety",
            "health", "employment", "benefits", "attendance", "leave",
            "recruitment", "confidentiality", "harassment"
        ]

    # src/utils/pdf_extractor.py
    # ... (all your imports and other methods are unchanged) ...

    def extract(self, pdf_path: str) -> Tuple[List[Dict], List[Dict]]:
        path = Path(pdf_path)
        semantic_chunks, positional_chunks = [], []

        if not path.exists():
            print(f"[ERROR] File not found: {pdf_path}")
            return semantic_chunks, positional_chunks

        doc = fitz.open(pdf_path)

        current_heading = "Untitled"
        buffer_lines = []

        for page_num, page in enumerate(doc, start=1):
            blocks = page.get_text("dict")["blocks"]
            if not blocks:  # scanned PDF
                blocks = self._ocr_page(page)

            avg_fontsize = self._compute_avg_fontsize(blocks)

            for block in blocks:
                if "lines" in block:  # Digital PDF
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            y0 = span.get("bbox", [0, 0, 0, 0])[1]
                            y1 = span.get("bbox", [0, 0, 0, 0])[3]

                            if not text:
                                continue

                            if self._is_heading(text, span, avg_fontsize):
                                if buffer_lines:
                                    semantic_chunks.append({
                                        "heading": current_heading,
                                        "text": " ".join([l["text"] for l in buffer_lines]).strip(),
                                        # --- 1. THE UPGRADE ---
                                        "page_number": buffer_lines[0]["page"]
                                    })
                                    buffer_lines.clear()
                                current_heading = text

                            buffer_lines.append({
                                "text": text,
                                "page": page_num,
                                "y0": y0,
                                "y1": y1
                            })
                            positional_chunks.append({
                                "page": page_num,
                                "y0": y0,
                                "y1": y1,
                                "text": text
                            })

                else:  # OCR lines
                    for line in block.get("lines", []):
                        text = line.get("text", "").strip()
                        y0 = line.get("y0", 0)
                        y1 = line.get("y1", y0 + 10)
                        if not text:
                            continue

                        if self._is_heading(text, line, avg_fontsize):
                            if buffer_lines:
                                semantic_chunks.append({
                                    "heading": current_heading,
                                    "text": " ".join([l["text"] for l in buffer_lines]).strip(),
                                    # --- 2. THE UPGRADE ---
                                    "page_number": buffer_lines[0]["page"]
                                })
                                buffer_lines.clear()
                            current_heading = text

                        buffer_lines.append({
                            "text": text,
                            "page": page_num,
                            "y0": y0,
                            "y1": y1
                        })
                        positional_chunks.append({
                            "page": page_num,
                            "y0": y0,
                            "y1": y1,
                            "text": text
                        })

        # Add final buffer
        if buffer_lines:
            semantic_chunks.append({
                "heading": current_heading,
                "text": " ".join([l["text"] for l in buffer_lines]).strip(),
                # --- 3. THE UPGRADE ---
                "page_number": buffer_lines[0]["page"]
            })
        positional_chunks = [line for line in positional_chunks if line["text"].strip()]
        if semantic_chunks and semantic_chunks[0]["heading"] == "Untitled":
            # ... (your logic) ...

            print(f"[INFO] Extracted {len(semantic_chunks)} semantic sections and {len(positional_chunks)} lines")
        return semantic_chunks, positional_chunks

    


    def _compute_avg_fontsize(self, blocks):
        sizes = []
        for block in blocks:
            for span in block.get("spans", []):
                sizes.append(span.get("size", 0))
        if sizes:
            return sum(sizes) / len(sizes)
        return 12  # default fallback

    def _is_heading(self, text, line, avg_fontsize):
        # Heuristic for headings
        font_size = line.get("size", avg_fontsize)
        # Size-based detection
        if font_size >= avg_fontsize * self.heading_font_multiplier:
            return True
        # Keyword detection
        for kw in self.heading_keywords:
            if kw.lower() in text.lower():
                return True
        # Title-case detection (at least 2 words)
        if len(text.split()) >= 2 and re.match(r"^([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)$", text):
            return True
        return False

    def _ocr_page(self, page):
        """Fallback OCR for scanned PDFs"""
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        lines = []
        n_boxes = len(ocr_data['level'])
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            if not text:
                continue
            lines.append({
                "text": text,
                "y0": ocr_data['top'][i],
                "y1": ocr_data['top'][i] + ocr_data['height'][i]
            })
        return [{"lines": lines}]

    def extract_from_folder(self, folder_path: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Extract chunks from all PDFs in a given folder.
    
        Returns combined semantic and positional chunks across all files.
        """
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            print(f"[ERROR] Folder not found: {folder_path}")
            return [], []
        
        all_semantic_chunks = []
        all_positional_chunks = []
        
        pdf_files = list(folder.glob("*.pdf"))
        if not pdf_files:
            print(f"[WARN] No PDF files found in {folder_path}")
            return [], []
        
        for pdf_file in pdf_files:
            print(f"[INFO] Processing {pdf_file.name} ...")
            semantic, positional = self.extract(str(pdf_file))
        
            # Attach filename context (useful later in FAISS metadata)
            for s in semantic:
                s["source_file"] = pdf_file.name
            for p in positional:
                p["source_file"] = pdf_file.name
        
            all_semantic_chunks.extend(semantic)
            all_positional_chunks.extend(positional)
        
        print(f"[INFO] ✅ Processed {len(pdf_files)} PDFs")
        print(f"[INFO] Total {len(all_semantic_chunks)} semantic sections and {len(all_positional_chunks)} positional lines extracted")
        
        return all_semantic_chunks, all_positional_chunks
        
