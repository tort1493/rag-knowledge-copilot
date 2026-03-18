from __future__ import annotations

from pathlib import Path

from project.rag.models import DocumentChunk


def chunk_text(
    text: str,
    source_file: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[DocumentChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be between 0 and chunk_size - 1")

    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks: list[DocumentChunk] = []
    start = 0
    index = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunk_text_value = cleaned[start:end].strip()
        if chunk_text_value:
            chunk_id = f"{Path(source_file).stem}-chunk-{index:03d}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    source_file=source_file,
                    text=chunk_text_value,
                    metadata={
                        "source_file": source_file,
                        "chunk_id": chunk_id,
                        "chunk_index": index,
                        "start_char": start,
                        "end_char": end,
                    },
                )
            )
        if end >= len(cleaned):
            break
        start = max(end - chunk_overlap, 0)
        index += 1
    return chunks


def load_markdown_chunks(
    knowledge_base_dir: Path,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path in sorted(knowledge_base_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        chunks.extend(
            chunk_text(
                text=text,
                source_file=path.name,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        )
    return chunks
