import chromadb
import uuid
from config import CHROMA_PATH, COLLECTION_NAME, TOP_K_RESULTS
from embedder import embed_texts, embed_single

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)

def store_chunks(chunks: list[dict]):
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    collection.add(
        ids=[str(uuid.uuid4()) for _ in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{
            "filename": c["filename"],
            "chunk_index": c["chunk_index"]
        } for c in chunks]
    )
    print(f"Stored {len(chunks)} chunks from {chunks[0]['filename']}")

def search(query: str) -> list[dict]:
    # Check collection is not empty first
    if collection.count() == 0:
        print("Collection is empty - no documents uploaded yet")
        return []

    query_embedding = embed_single(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(TOP_K_RESULTS, collection.count()),
        include=["documents", "metadatas", "distances"]  # must include all three
    )

    # Safety check
    if not results or not results.get("documents") or not results["documents"][0]:
        print("No results returned from ChromaDB")
        return []

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        print(f"Chunk from {meta['filename']} | distance: {dist:.4f}")
        chunks.append({
            "text": doc,
            "filename": meta["filename"]
        })

    return chunks

def list_documents() -> list[str]:
    results = collection.get()
    if not results["metadatas"]:
        return []
    filenames = list(set(m["filename"] for m in results["metadatas"]))
    return filenames