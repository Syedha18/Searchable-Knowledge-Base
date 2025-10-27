from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pathlib import Path
import json

from src.pdf_processor import PDFProcessor
from src.image_captioner import ImageCaptioner

# Initialize FastAPI app
app = FastAPI(title="PDF Content Extractor", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount output directory for file access
app.mount("/output", StaticFiles(directory="output"), name="output")

# Initialize image captioner (lazy loading)
captioner = None


def get_captioner():
    """Lazy load the image captioner"""
    global captioner
    if captioner is None:
        captioner = ImageCaptioner()
    return captioner


@app.get("/")
async def root():
    """Serve the HTML frontend"""
    return FileResponse("index.html")


@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "message": "PDF Content Extractor API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload - Upload PDF file for processing",
            "health": "/health - Check API health status"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "PDF Content Extractor"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process PDF file
    
    Extracts:
    - Images
    - Tables (as CSV)
    - Charts/Graphs
    - Generates descriptions for extracted images
    """
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file
    pdf_path = UPLOAD_DIR / file.filename
    
    try:
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    finally:
        file.file.close()
    
    # Process PDF
    try:
        processor = PDFProcessor(str(pdf_path), output_dir=str(OUTPUT_DIR))
        results = processor.process_all()
        
        # Generate captions for extracted images
        image_paths = [img["path"] for img in results["images"]]
        
        if image_paths:
            img_captioner = get_captioner()
            captions = img_captioner.generate_captions_batch(image_paths)
            
            # Add captions to results
            for i, img_data in enumerate(results["images"]):
                img_data["description"] = captions[i]["caption"]
        
        # Prepare response
        response = {
            "status": "success",
            "filename": file.filename,
            "extracted_content": {
                "images": {
                    "count": len(results["images"]),
                    "items": results["images"]
                },
                "tables": {
                    "count": len(results["tables"]),
                    "items": results["tables"]
                },
                "charts": {
                    "count": len(results["charts"]),
                    "items": results["charts"]
                }
            }
        }
        
        # Save results to JSON
        results_path = OUTPUT_DIR / f"{file.filename}_results.json"
        with open(results_path, "w") as f:
            json.dump(response, f, indent=2)
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    # Fixed for localhost
    uvicorn.run(app, host="127.0.0.1", port=8000)
