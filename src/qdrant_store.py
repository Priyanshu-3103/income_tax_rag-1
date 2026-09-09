from pathlib import Path
import re

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


# -----------------------------
# Configuration
# -----------------------------

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "income_tax_rules_2026"

CHUNKS_FILE = Path("data/chunks.txt")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# -----------------------------
# Load chunks with page metadata
# -----------------------------

def load_chunks():

    print("Loading chunks...")

    text = CHUNKS_FILE.read_text(encoding="utf-8")

    raw_chunks = text.split("--- CHUNK ")

    chunks = []

    for raw_chunk in raw_chunks:

        raw_chunk = raw_chunk.strip()

        if not raw_chunk:
            continue

        # Find page number
        page_match = re.search(
            r"--- PAGE (\d+) ---",
            raw_chunk
        )

        if page_match:
            page = int(page_match.group(1))
        else:
            page = None

        # Remove chunk number
        lines = raw_chunk.splitlines()

        if lines:
            lines = lines[1:]

        # Remove page marker from actual text
        text_lines = []

        for line in lines:

            if not line.startswith("--- PAGE "):
                text_lines.append(line)

        chunk_text = "\n".join(text_lines).strip()

        if not chunk_text:
            continue

        chunks.append({
            "chunk_id": len(chunks),
            "page": page,
            "text": chunk_text,
        })

    print(f"Total chunks loaded: {len(chunks)}")

    return chunks


# -----------------------------
# Main
# -----------------------------

def main():

    # -----------------------------
    # Load embedding model
    # -----------------------------

    print("Loading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    # Get embedding dimension
    test_embedding = model.encode("test")

    vector_size = len(test_embedding)

    print(f"Embedding dimension: {vector_size}")

    # -----------------------------
    # Connect to Qdrant
    # -----------------------------

    print("Connecting to Qdrant...")

    client = QdrantClient(
        url=QDRANT_URL
    )

    # -----------------------------
    # Delete old collection
    # -----------------------------

    if client.collection_exists(COLLECTION_NAME):

        print(f"Collection '{COLLECTION_NAME}' already exists.")

        print("Deleting old collection...")

        client.delete_collection(
            COLLECTION_NAME
        )

    # -----------------------------
    # Create collection
    # -----------------------------

    print("Creating Qdrant collection...")

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    # -----------------------------
    # Load chunks
    # -----------------------------

    chunks = load_chunks()

    # -----------------------------
    # Create embeddings
    # -----------------------------

    print("Creating embeddings...")

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
        normalize_embeddings=True,
    )

    # -----------------------------
    # Prepare Qdrant points
    # -----------------------------

    points = []

    for chunk, embedding in zip(chunks, embeddings):

        points.append(
            PointStruct(
                id=chunk["chunk_id"],
                vector=embedding.tolist(),
                payload={
                    "text": chunk["text"],
                    "chunk_id": chunk["chunk_id"],
                    "page": chunk["page"],
                    "source": "Income-tax Rules, 2026",
                },
            )
        )

    # -----------------------------
    # Upload to Qdrant
    # -----------------------------

    print("Uploading vectors to Qdrant...")

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    print()
    print("=" * 50)
    print("QDRANT SETUP COMPLETE")
    print("=" * 50)

    print(f"Collection: {COLLECTION_NAME}")
    print(f"Vectors uploaded: {len(points)}")
    print(f"Vector dimension: {vector_size}")

    print()
    print("Income-tax Rules 2026 is now stored in Qdrant.")
    print("Page metadata has also been stored.")


if __name__ == "__main__":
    main()