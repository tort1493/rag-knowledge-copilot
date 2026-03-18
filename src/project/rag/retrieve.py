from __future__ import annotations

from pathlib import Path

from project.rag.index import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_EMBEDDING_MODEL,
    embed_texts,
    get_chroma_client,
    get_or_create_collection,
)
from project.rag.models import RetrievedChunk


def distance_to_score(distance: float) -> float:
    return max(0.0, min(1.0, 1.0 - distance))


def retrieve_chunks(
    question: str,
    index_dir: Path,
    top_k: int = 3,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> list[RetrievedChunk]:
    client = get_chroma_client(index_dir)
    collection = get_or_create_collection(client, collection_name=collection_name)
    if collection.count() == 0:
        return []

    question_embedding = embed_texts([question], model=embedding_model)[0]
    result = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    retrieved: list[RetrievedChunk] = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        source_file = str(metadata.get("source_file", "unknown"))
        chunk_id = str(metadata.get("chunk_id", "unknown"))
        retrieved.append(
            RetrievedChunk(
                chunk_id=chunk_id,
                source_file=source_file,
                text=document,
                score=distance_to_score(float(distance)),
                metadata=dict(metadata),
            )
        )
    return retrieved


def filter_retrieved_chunks(
    chunks: list[RetrievedChunk],
    score_threshold: float,
) -> list[RetrievedChunk]:
    return [chunk for chunk in chunks if chunk.score >= score_threshold]
