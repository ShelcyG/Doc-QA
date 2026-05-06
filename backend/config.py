import os
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./data/chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama3.2:1b"