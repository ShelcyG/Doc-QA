from config import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_text(text: str, filename: str) -> list[dict]:
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + CHUNK_SIZE
        chunk_words = words[start:end]
        chunk_str = " ".join(chunk_words)

        if chunk_str.strip():
            chunks.append({
                "text": chunk_str,
                "filename": filename,
                "chunk_index": len(chunks)
            })

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks

if __name__ == "__main__":
    sample = "word " * 1200
    chunks = chunk_text(sample, "test.txt")
    print(f"Total chunks: {len(chunks)}")
    print(f"First chunk preview: {chunks[0]['text'][:100]}")