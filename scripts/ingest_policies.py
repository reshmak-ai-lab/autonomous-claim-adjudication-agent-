from pathlib import Path


POLICY_DIR = Path("data/policies")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - CHUNK_OVERLAP

    return chunks


def ingest_policies():
    policy_files = sorted(POLICY_DIR.glob("*.txt"))

    if not policy_files:
        raise FileNotFoundError(
            f"No policy files found in {POLICY_DIR}"
        )

    processed_policies = 0
    total_chunks = 0

    print("=" * 60)
    print("POLICY INGESTION")
    print("=" * 60)

    for policy_file in policy_files:
        print(f"\nProcessing: {policy_file.name}")

        text = policy_file.read_text(
            encoding="utf-8"
        ).strip()

        if not text:
            print(f"WARNING: {policy_file.name} is empty")
            continue

        chunks = chunk_text(text)

        if not chunks:
            print(f"WARNING: No chunks created for {policy_file.name}")
            continue

        processed_policies += 1
        total_chunks += len(chunks)

        print(f"  Chunks: {len(chunks)}")

    print("\n" + "=" * 60)
    print("Policy ingestion completed")
    print(f"Policies processed: {processed_policies}")
    print(f"Chunks created: {total_chunks}")
    print("=" * 60)


if __name__ == "__main__":
    ingest_policies()