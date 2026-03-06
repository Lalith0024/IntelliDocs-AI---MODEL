import os


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Basic word-based chunker with slightly larger chunks for better context."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def extract_text(file_path: str) -> str:
    """Extract text from TXT, PDF, JSON, or CSV files."""
    ext = os.path.splitext(file_path)[1].lower()
    
    print(f"DEBUG: Processing file extraction for {file_path} (Extension: {ext})")
    
    if ext == ".pdf":
        import fitz
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text.strip()
        except Exception as e:
            print(f"CRITICAL: PDF Extraction failed for {file_path}. Error: {e}")
            return ""

    elif ext == ".json":
        try:
            import json
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        except Exception as e:
            print(f"CRITICAL: JSON Extraction failed for {file_path}. Error: {e}")
            return ""

    elif ext == ".csv":
        try:
            import csv
            content = []
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    content.append(" | ".join(row))
            return "\n".join(content)
        except Exception as e:
            print(f"CRITICAL: CSV Extraction failed for {file_path}. Error: {e}")
            return ""

    elif ext in [".png", ".jpg", ".jpeg"]:
        # If OCR isn't available, we'll try a basic metadata or fallback
        # In a real environment, we'd use pytesseract or EasyOCR
        return f"[Image File: {os.path.basename(file_path)} - OCR not yet implemented but file accepted.]"

    else:
        # Default to TXT
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"CRITICAL: TXT Extraction failed for {file_path}. Error: {e}")
            return ""
