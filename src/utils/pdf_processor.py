"""
PDF Processor Module
Extracts images, tables, charts, and graphs from PDF files
"""
import fitz  # PyMuPDF
import pdfplumber
from PIL import Image
import io
from pathlib import Path


class PDFProcessor:
    """Handle PDF content extraction"""
    
    def __init__(self, pdf_path, output_dir="output"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.tables_dir = self.output_dir / "tables"
        self.charts_dir = self.output_dir / "charts"
        
        # Create output directories
        for dir_path in [self.images_dir, self.tables_dir, self.charts_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def extract_images(self, min_width=100, min_height=100, min_bytes=2048):
        """Extract images from PDF, skipping tiny logos/signatures"""
        extracted_images = []
    
        try:
            pdf_document = fitz.open(self.pdf_path)
    
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                image_list = page.get_images(full=True)
    
                for img_index, img_info in enumerate(image_list):
                    xref = img_info[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    width = int(base_image.get("width", 0))
                    height = int(base_image.get("height", 0))
                    
                    # --- Filters ---
                    if width < min_width or height < min_height:
                        continue  
                    if len(image_bytes) < min_bytes:
                        continue
    
                    # Save the image
                    image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
                    image_path = self.images_dir / image_filename
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)
    
                    extracted_images.append({
                        "filename": image_filename,
                        "path": str(image_path),
                        "page": page_num + 1,
                        "format": image_ext,
                        "width": width,
                        "height": height
                    })
    
            pdf_document.close()
            return extracted_images
    
        except Exception as e:
            print(f"Error extracting images: {e}")
            return []


    def extract_tables(self):
        """Extract tables from PDF using pdfplumber"""
        extracted_tables = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract tables from the page
                    tables = page.extract_tables()
                    
                    for table_index, table in enumerate(tables):
                        if table:  # Check if table is not empty
                            # Save table as CSV
                            table_filename = f"page{page_num + 1}_table{table_index + 1}.csv"
                            table_path = self.tables_dir / table_filename
                            
                            # Write table to CSV
                            import csv
                            with open(table_path, "w", newline="", encoding="utf-8") as f:
                                writer = csv.writer(f)
                                writer.writerows(table)
                            
                            extracted_tables.append({
                                "filename": table_filename,
                                "path": str(table_path),
                                "page": page_num + 1,
                                "rows": len(table),
                                "columns": len(table) if table else 0
                            })
            
            return extracted_tables
            
        except Exception as e:
            print(f"Error extracting tables: {e}")
            return []
    
    def _contains_visual_elements(self, page):
        """
        Simple heuristic to check if page contains charts/graphs
        Checks for drawings, paths, or multiple images
        """
        # Get drawings on the page
        drawings = page.get_drawings()
        images = page.get_images()
        
        # If page has drawings or multiple images, likely contains charts
        return len(drawings) > 10 or len(images) > 1
    
    def process_all(self):
        """Extract all content from PDF"""
        results = {
            "images": self.extract_images(),
            "tables": self.extract_tables(),
        }
        return results
