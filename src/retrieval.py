from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "income_tax_rules_2026"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

TOP_K = 5
SCORE_THRESHOLD = 0.35

model = SentenceTransformer(MODEL_NAME, device="cpu")
client = QdrantClient(url=QDRANT_URL)


def retrieve(query: str, top_k: int = TOP_K):

    query_vector = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True
    )

    retrieved = []

    for result in results.points:

        score = result.score

        if score < SCORE_THRESHOLD:
            continue

        payload = result.payload

        retrieved.append({
            "score": score,
            "chunk_id": payload.get("chunk_id"),
            "page": payload.get("page"),
            "text": payload.get("text"),
            "source": payload.get("source")
        })

    return retrieved


if __name__ == "__main__":

    question = input("\nEnter your Income-tax question: ")

    results = retrieve(question)

    print("\n" + "=" * 70)
    print("RETRIEVAL RESULTS")
    print("=" * 70)

    if not results:

        print("\nNo sufficiently relevant information found.")
        print("The system will not answer this question.")

    else:

        for i, result in enumerate(results, start=1):

            print(f"\n--- Result {i} ---")
            print(f"Score    : {result['score']:.4f}")
            print(f"PDF Page : {result['page']}")
            print(f"Chunk ID  : {result['chunk_id']}")
            print(f"Source   : {result['source']}")

            print("\nText:")
            print(result["text"])