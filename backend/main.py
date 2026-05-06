import shutil
import os
import ollama
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from config import LLM_MODEL
from file_processor import extract_text
from chunker import chunk_text
from vector_store import store_chunks, list_documents, search

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QuestionRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = extract_text(file_path, file.filename)
    if not text.strip():
        raise HTTPException(400, "Could not extract text from file")

    chunks = chunk_text(text, file.filename)
    store_chunks(chunks)

    return {
        "message": f"Successfully uploaded {file.filename}",
        "chunks_stored": len(chunks)
    }

@app.get("/documents")
def get_documents():
    return {"documents": list_documents()}

@app.post("/ask")
async def ask_question(payload: QuestionRequest):
    try:
        question = payload.question.strip()

        if not question:
            raise HTTPException(400, "Question cannot be empty")

        print(f"Question received: {question}")

        relevant_chunks = search(question)
        print(f"Found {len(relevant_chunks)} chunks")

        if not relevant_chunks:
            return {
                "answer": "No relevant documents found. Please upload some documents first.",
                "sources": []
            }

        context = "\n\n".join([
            f"[From: {c['filename']}]\n{c['text']}"
            for c in relevant_chunks
        ])

        prompt = f"""You are a helpful assistant that answers questions based on the provided document excerpts.
Use ONLY the information from the documents below to answer the question.
If the answer is not found in the documents, say "I could not find this information in the uploaded documents."

Documents:
{context}

Question: {question}

Answer:"""

        print("Calling Ollama LLM...")

        response = ollama.chat(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response["message"]["content"].strip()
        print(f"Answer generated: {answer[:100]}")

        sources = list(set(c["filename"] for c in relevant_chunks))

        return {"answer": answer, "sources": sources}

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in /ask: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("../frontend/index.html")