"""
Utility functions for the PDF extractor
"""
import os
from pathlib import Path


def ensure_dir(directory):
    """Ensure directory exists, create if it doesn't"""
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_file_size(filepath):
    """Get file size in MB"""
    size_bytes = os.path.getsize(filepath)
    size_mb = size_bytes / (1024 * 1024)
    return round(size_mb, 2)


def validate_pdf(filepath):
    """Validate if file is a PDF"""
    return filepath.lower().endswith('.pdf')
