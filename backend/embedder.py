import requests
from config import HF_API_KEY, EMBEDDING_MODEL

# Updated URL - HuggingFace moved to router endpoint
API_URL = f"https://router.huggingface.co/hf-inference/models/{EMBEDDING_MODEL}/pipeline/feature-extraction"
HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

def embed_texts(texts: list[str]) -> list[list[float]]:
    print(f"Embedding {len(texts)} texts...")

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json={"inputs": texts},
        timeout=30
    )

    print(f"Status code: {response.status_code}")

    if response.status_code != 200:
        raise ValueError(f"HuggingFace API error {response.status_code}: {response.text}")

    result = response.json()

    if isinstance(result, dict) and "error" in result:
        raise ValueError(f"HuggingFace embedding error: {result['error']}")

    # Handle [batch][tokens][dim] shape — mean pool across tokens
    if isinstance(result[0], list):
        if isinstance(result[0][0], list):
            embeddings = []
            for item in result:
                avg = [sum(col) / len(col) for col in zip(*item)]
                embeddings.append(avg)
            return embeddings
        else:
            return result
    else:
        return [result]

def embed_single(text: str) -> list[float]:
    return embed_texts([text])[0]


if __name__ == "__main__":
    print("Testing embedder...")
    result = embed_single("hello world this is a test")
    print(f"✅ Embedding size: {len(result)}")
    print(f"First 5 values: {result[:5]}")