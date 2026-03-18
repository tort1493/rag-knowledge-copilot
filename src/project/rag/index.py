from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable

from project.rag.chunking import load_markdown_chunks
from project.rag.models import DocumentChunk

DEFAULT_COLLECTION_NAME = "knowledge_base"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def get_openai_client() -> Any:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)


def get_chroma_client(index_dir: Path) -> Any:
    import chromadb

    index_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(index_dir))


def get_or_create_collection(
    client: Any,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> Any:
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def embed_texts(
    texts: Iterable[str],
    model: str = DEFAULT_EMBEDDING_MODEL,
    client: Any | None = None,
) -> list[list[float]]:
    openai_client = client or get_openai_client()
    response = openai_client.embeddings.create(model=model, input=list(texts))
    return [item.embedding for item in response.data]


def reset_collection(
    client: Any,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> None:
    try:
        client.delete_collection(collection_name)
    except Exception:
        return


def index_chunks(
    chunks: list[DocumentChunk],
    index_dir: Path,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> int:
    client = get_chroma_client(index_dir)
    reset_collection(client, collection_name=collection_name)
    collection = get_or_create_collection(client, collection_name=collection_name)
    embeddings = embed_texts([chunk.text for chunk in chunks], model=embedding_model)
    collection.add(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadatas=[chunk.metadata for chunk in chunks],
        embeddings=embeddings,
    )
    return len(chunks)


def build_index(
    knowledge_base_dir: Path,
    index_dir: Path,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> dict[str, int]:
    chunks = load_markdown_chunks(
        knowledge_base_dir=knowledge_base_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    count = index_chunks(
        chunks=chunks,
        index_dir=index_dir,
        collection_name=collection_name,
        embedding_model=embedding_model,
    )
    return {"documents": len(list(knowledge_base_dir.glob('*.md'))), "chunks": count}
