**Document Q&A System**

UPLOAD PIPELINE
───────────────────────────────────────────────
User selects file in browser
        ↓
POST /upload  →  FastAPI receives file
        ↓
file_processor.py
  PDF      → pdfplumber     → plain text
  DOCX     → python-docx    → plain text
  CSV/XLSX → pandas         → plain text
  TXT      → direct read    → plain text
  Image    → pytesseract    → plain text (OCR)
  Audio    → Whisper        → plain text (transcription)
        ↓
chunker.py
  Split text into 500-word chunks
  with 50-word overlap between chunks
        ↓
embedder.py
  HuggingFace API converts each chunk
  into a 384-dimensional vector
        ↓
vector_store.py
  ChromaDB stores vectors + text + filename
  permanently on disk (survives restarts)

QUERY PIPELINE
───────────────────────────────────────────────
User types question in browser
        ↓
POST /ask  →  FastAPI receives question
        ↓
embedder.py
  HuggingFace API converts question
  into a 384-dimensional vector
        ↓
vector_store.py
  ChromaDB finds top 5 most similar
  chunks using cosine similarity
        ↓
main.py builds prompt:
  "Answer using only these document excerpts:
   [chunk 1] [chunk 2] ... [chunk 5]
   Question: ..."
        ↓
Ollama llama3.2:1b
  Generates answer from context only
        ↓
Answer + source filenames → browser
