"""
PDF Processor Module
Extracts images, tables, charts, and graphs from PDF files
"""
import fitz  # PyMuPDF
import pdfplumber
from PIL import Image
import io
import os
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
    
    def extract_images(self):
        """Extract all images from PDF using PyMuPDF"""
        extracted_images = []
        
        try:
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(self.pdf_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # Get list of images on the page
                image_list = page.get_images(full=True)
                
                for img_index, img_info in enumerate(image_list):
                    xref = img_info
                    
                    # Extract image
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Save image
                    image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
                    image_path = self.images_dir / image_filename
                    
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    extracted_images.append({
                        "filename": image_filename,
                        "path": str(image_path),
                        "page": page_num + 1,
                        "format": image_ext
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
    
    def extract_charts_and_graphs(self):
        """
        Extract charts and graphs from PDF
        Uses image extraction and filters for chart-like content
        """
        extracted_charts = []
        
        try:
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(self.pdf_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # Get page as image for better chart detection
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for quality
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Check if page contains visual elements (simple heuristic)
                # In a real scenario, you might use ML models to detect charts
                if self._contains_visual_elements(page):
                    chart_filename = f"page{page_num + 1}_chart.png"
                    chart_path = self.charts_dir / chart_filename
                    
                    img.save(chart_path, "PNG")
                    
                    extracted_charts.append({
                        "filename": chart_filename,
                        "path": str(chart_path),
                        "page": page_num + 1,
                        "type": "visual_content"
                    })
            
            pdf_document.close()
            return extracted_charts
            
        except Exception as e:
            print(f"Error extracting charts: {e}")
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
            "charts": self.extract_charts_and_graphs()
        }
        return results
