Intelligent Document Assistant MVP
A local, single-user document assistant that lets users upload files, persist the processed content, and ask document-grounded questions across everything they have uploaded.
Upload file
    ↓
Extract text
(pdfplumber / python-docx / pandas / pytesseract / Whisper)
    ↓
Chunk text
(500-word chunks, 50-word overlap — chunker.py)
    ↓
Create embeddings
(HuggingFace API — sentence-transformers/all-MiniLM-L6-v2)
    ↓
Store in ChromaDB
(vectors + text + filename saved to disk permanently)
