from pathlib import Path
from pypdf import PdfReader


PDF_PATH = Path("data/En-Notified-IT-Rules-2026-20-03-2026.pdf")
OUTPUT_PATH = Path("data/chunks.txt")

CHUNK_SIZE = 1200
OVERLAP = 200


def extract_pages(pdf_path):
    """Extract text while preserving page numbers."""

    reader = PdfReader(str(pdf_path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        text = text.strip()

        if text:
            pages.append({
                "page": page_number,
                "text": text
            })

    return pages


def create_chunks(pages):
    """Create chunks while preserving their source page."""

    chunks = []

    for page_data in pages:

        page_number = page_data["page"]
        words = page_data["text"].split()

        start = 0

        while start < len(words):

            end = min(start + CHUNK_SIZE, len(words))

            chunk_text = " ".join(words[start:end])

            chunks.append({
                "chunk_id": len(chunks),
                "page": page_number,
                "text": chunk_text
            })

            if end >= len(words):
                break

            start = end - OVERLAP

    return chunks


def save_chunks(chunks):

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:

        for chunk in chunks:

            f.write(f"--- CHUNK {chunk['chunk_id']} ---\n")
            f.write(f"--- PAGE {chunk['page']} ---\n")
            f.write(chunk["text"])
            f.write("\n\n")


def main():

    print("Reading PDF...")

    pages = extract_pages(PDF_PATH)

    print(f"Extracted {len(pages)} pages.")

    print("Creating chunks...")

    chunks = create_chunks(pages)

    print(f"Created {len(chunks)} chunks.")

    save_chunks(chunks)

    print(f"Saved chunks to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()