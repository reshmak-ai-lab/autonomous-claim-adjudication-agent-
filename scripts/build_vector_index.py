#from pathlib import Path
from app.rag.rag_ingestion import (
    PolicyLoader,
    PolicyChunker,
    MetadataBuilder,
)

from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore

def main():

    print("=" * 60)
    print("BUILDING POLICY VECTOR INDEX")
    print("=" * 60)

    loader = PolicyLoader()

    documents = loader.load()

    print(f"Policies loaded: {len(documents)}")

    chunker = PolicyChunker(
        chunk_size=1000,
        chunk_overlap=100,
    )

    chunks = chunker.chunk_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    metadata_builder = MetadataBuilder()

    metadata = []

    for chunk in chunks:
        item = metadata_builder.build(chunk)
        item["text"] = chunk["text"]
        metadata.append(item)

    embedding_service = EmbeddingService()

    print("Generating embeddings...")

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embedding_service.embed(texts)

    print(f"Embeddings generated: {len(embeddings)}")

    vector_store = VectorStore()

    vector_store.build(
        embeddings=embeddings,
        metadata=metadata,
    )

    vector_store.save()

    print("\n" + "=" * 60)
    print("VECTOR INDEX BUILD COMPLETED")
    print(f"Policies: {len(documents)}")
    print(f"Chunks: {len(chunks)}")
    print("=" * 60)


if __name__ == "__main__":
    main()