# 📄 Document Q&A System

An intelligent document assistant that lets you upload documents and ask questions in natural language. Uses semantic search to find relevant content and a local LLM to generate accurate answers — completely free with no cloud costs.

---

## 🔄 Core Flow

```
UPLOAD:
upload file → extract text → chunk text → create embeddings → store in ChromaDB

QUERY:
ask question → embed question → retrieve relevant chunks → generate answer with Ollama → return answer + sources
```

---

## ✨ What It Does

- Upload documents — TXT, PDF, DOCX, CSV, XLSX, Images, Audio/Voice
- Ask questions in a simple chat interface
- Get answers with source file references
- Documents persist permanently across server restarts
- Every question searches across ALL uploaded documents

---

## 🛠️ Tools Used

| Layer | Tool | Purpose |
|---|---|---|
| **Backend** | FastAPI (Python) | REST API — upload, search, answer |
| **LLM** | Ollama `llama3.2:1b` | Generate answers locally — free |
| **Embeddings** | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` | Convert text to vectors |
| **Vector DB** | ChromaDB PersistentClient | Store and search vectors on disk |
| **Audio** | OpenAI Whisper `base` | Transcribe audio to text locally |
| **PDF** | pdfplumber | Extract text from PDFs |
| **Word** | python-docx | Extract text from DOCX files |
| **CSV/Excel** | pandas | Convert tabular data to text |
| **Image OCR** | Tesseract + pytesseract | Extract text from images |
| **Frontend** | Vanilla HTML/CSS/JS | Upload panel + chat interface |

---

## 🏗️ Architecture

```
UPLOAD PIPELINE
────────────────────────────────────────
User selects file
        ↓
POST /upload → FastAPI
        ↓
file_processor.py
  PDF      → pdfplumber
  DOCX     → python-docx
  CSV/XLSX → pandas
  TXT      → direct read
  Image    → Tesseract OCR
  Audio    → Whisper transcription
        ↓
chunker.py → 500-word chunks, 50-word overlap
        ↓
embedder.py → HuggingFace API → 384-dim vectors
        ↓
vector_store.py → ChromaDB saves to disk permanently

QUERY PIPELINE
────────────────────────────────────────
User types question
        ↓
POST /ask → FastAPI
        ↓
embedder.py → HuggingFace API → 384-dim vector
        ↓
vector_store.py → ChromaDB → top 5 similar chunks
        ↓
Prompt = instruction + chunks + question
        ↓
Ollama llama3.2:1b → generates answer
        ↓
Answer + source filenames → browser
```

---

## 📁 Project Structure

```
doc-qa/
├── backend/
│   ├── main.py            # FastAPI endpoints
│   ├── config.py          # Central config
│   ├── file_processor.py  # Text extraction per format
│   ├── chunker.py         # Split text into chunks
│   ├── embedder.py        # HuggingFace embeddings
│   └── vector_store.py    # ChromaDB operations
├── frontend/
│   └── index.html         # Upload panel + chat UI
├── data/
│   ├── chroma_db/         # Vector store (auto-created)
│   └── uploads/           # Uploaded files (auto-created)
├── sample_docs/
│   ├── sample1.txt        # Company info
│   ├── sample2.csv        # Employee data
│   └── sample3.docx       # Return policy
├── .env                   # API keys (not in git)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ✅ Prerequisites

### 1. Python 3.10+
[python.org](https://python.org)

### 2. Ollama
[ollama.com](https://ollama.com) — then pull the model:
```bash
ollama pull llama3.2:1b
```

### 3. ffmpeg (for audio)
```bash
# Windows
winget install --id Gyan.FFmpeg -e --source winget

# Mac
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

Verify: `ffmpeg -version`

### 4. Tesseract OCR (for images, optional)
- Windows: [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- Mac: `brew install tesseract`
- Linux: `sudo apt install tesseract-ocr`

### 5. HuggingFace API Key (free)
1. Sign up at [huggingface.co](https://huggingface.co)
2. Settings → Access Tokens → New Token → Fine-grained
3. Enable: ✅ Read access to repos + ✅ Make calls to Inference Providers
4. Copy the token

---

## 🚀 Setup & Running

### Step 1 — Clone
```bash
git clone https://github.com/yourusername/doc-qa.git
cd doc-qa
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Create `.env` in root `doc-qa/` folder
```
HF_API_KEY=your_huggingface_token_here
CHROMA_PATH=./data/chroma_db
COLLECTION_NAME=documents
```

### Step 4 — Start Ollama (Terminal 1)
```bash
ollama serve
```
Keep this running in the background.

### Step 5 — Start server (Terminal 2)
```bash
cd backend
python -m uvicorn main:app --reload
```

You should see:
```
Loading Whisper model...
Whisper model loaded!
INFO: Application startup complete.
```

### Step 6 — Open browser
```
http://localhost:8000
```

---

## 🧪 How to Test

### Sample documents
| File | Content |
|---|---|
| `sample1.txt` | Company info — John Smith, 2010, San Francisco |
| `sample2.csv` | Employees — names, departments, salaries |
| `sample3.docx` | Return policy — 30 days, refund process |

### Questions to try
```
"Who founded the company?"        → John Smith, 2010 (sample1.txt)
"What is John Smith's salary?"    → $90,000 (sample2.csv)
"What is the return policy?"      → 30 days (sample3.docx)
"How do I contact support?"       → support@company.com (sample3.docx)
"Tell me about John Smith"        → pulls from sample1.txt AND sample2.csv
```

### curl commands
```bash
# Upload file
curl -X POST http://localhost:8000/upload -F "file=@sample_docs/sample1.txt"

# List documents
curl http://localhost:8000/documents

# Ask question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "who founded the company"}'

# Upload audio
curl -X POST http://localhost:8000/upload \
  -F "file=@sample_docs/recording.m4a" --max-time 120
```

### Test persistence
```bash
# Upload
curl -X POST http://localhost:8000/upload -F "file=@sample_docs/sample1.txt"

# Stop server Ctrl+C then restart
python -m uvicorn main:app --reload

# Ask without uploading again — must still answer
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "who founded the company"}'
```

### Test cross-document search
```bash
# Upload both files
curl -X POST http://localhost:8000/upload -F "file=@sample_docs/sample1.txt"
curl -X POST http://localhost:8000/upload -F "file=@sample_docs/sample2.csv"

# Answer should pull from BOTH files
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "tell me everything about john smith"}'
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Frontend UI |
| `POST` | `/upload` | Upload a document |
| `GET` | `/documents` | List uploaded documents |
| `POST` | `/ask` | Ask a question |

### POST /upload response
```json
{
  "message": "Successfully uploaded sample1.txt",
  "chunks_stored": 3
}
```

### GET /documents response
```json
{
  "documents": ["sample1.txt", "sample2.csv", "sample3.docx"]
}
```

### POST /ask request + response
```json
// Request
{ "question": "who founded the company" }

// Response
{
  "answer": "The company was founded by John Smith in 2010 in San Francisco.",
  "sources": ["sample1.txt"]
}
```

---

## 📂 Supported Formats

| Format | Extensions | Method |
|---|---|---|
| Plain text | `.txt` | Direct read |
| PDF | `.pdf` | pdfplumber |
| Word | `.docx`, `.doc` | python-docx |
| CSV | `.csv` | pandas (auto encoding) |
| Excel | `.xlsx`, `.xls` | pandas |
| Images | `.png`, `.jpg`, `.jpeg` | Tesseract OCR |
| Audio | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` | Whisper |

---

## 🧠 Design Decisions

**Why ChromaDB?**
Zero infrastructure — no Docker, no cloud. `PersistentClient` saves to disk automatically. For production with multiple users we'd migrate to Pinecone or Weaviate.

**Why 500-word chunks with 50-word overlap?**
LLMs can't process full documents at once. Chunking retrieves only the 5 most relevant pieces per question. Overlap prevents important sentences from being cut at boundaries.

**Why same embedding model for documents and queries?**
Cosine similarity only works in the same vector space. Different models would produce incompatible vectors and break semantic search.

**Why HuggingFace for embeddings?**
`all-MiniLM-L6-v2` is purpose-built for semantic similarity. Free tier handles MVP volume. For production we'd switch to fastembed for fully local embeddings with no API dependency.

**Why Ollama for LLM?**
100% local — no API key, no internet, no cost. For production we'd use Groq's hosted `llama-3.3-70b` for faster responses and better quality.

**Why Whisper for audio?**
Runs fully locally, no API key needed. Once audio is transcribed it flows through the exact same pipeline as every other format.

---

## ⚖️ Trade-offs for MVP

| Area | MVP | Production |
|---|---|---|
| Users | Single user, no auth | JWT auth + per-user namespacing |
| LLM | Ollama local `llama3.2:1b` | Groq `llama-3.3-70b` |
| Embeddings | HuggingFace API | fastembed local ONNX |
| File processing | Synchronous | Async (Celery + Redis) |
| Vector DB | ChromaDB local | Pinecone / Weaviate |
| Chat history | None | Session-based memory |
| Doc management | Upload only | Full CRUD |
| Frontend | Vanilla HTML | React + Tailwind |
| Deployment | Local | Docker + cloud |

---

## 📈 Scaling for Production

**Short term:**
- Groq for LLM — `llama-3.3-70b`, much faster and smarter
- fastembed for local embeddings — removes HuggingFace API dependency
- Async file processing with Celery + Redis
- User authentication with per-user ChromaDB namespacing

**Medium term:**
- Pinecone or Weaviate for scalable vector search
- Document management — delete, update, re-index
- Conversation memory with session IDs in Redis
- Streaming responses — answers appear word by word

**Long term:**
- Docker + Kubernetes with auto-scaling
- Fine-tune embedding model on domain-specific data
- Multi-tenancy with proper data isolation
- Analytics dashboard

---

## 🔧 Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `Could not extract text` | File empty or corrupted | Recreate and re-upload |
| `No relevant documents found` | Nothing uploaded | Upload a document first |
| `500 on /ask` | Ollama not running | Run `ollama serve` |
| `Embedding 403` | HF token missing permission | Regenerate with Inference Providers enabled |
| `Audio transcription error` | ffmpeg not in PATH | Install ffmpeg, restart terminal |
| `Image returns empty` | Tesseract not installed | Install Tesseract |
| `Could not import module main` | Wrong folder | Run uvicorn from inside `backend/` |
| `Read timed out` | HF API slow | Increase timeout to 120 in embedder.py |

---

## 📦 requirements.txt

```
fastapi
uvicorn
python-dotenv
requests
ollama
chromadb
pdfplumber
python-docx
pandas
openpyxl
pillow
pytesseract
python-multipart
openai-whisper
```
