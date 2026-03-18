from pathlib import Path

from project.rag.chunking import chunk_text


def test_chunking_emits_stable_ids_and_metadata() -> None:
    text = "A" * 1200 + "B" * 1200
    chunks = chunk_text(text=text, source_file="policy.md", chunk_size=1000, chunk_overlap=150)

    assert len(chunks) >= 2
    assert chunks[0].chunk_id == "policy-chunk-000"
    assert chunks[0].metadata["source_file"] == "policy.md"
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[1].chunk_id == "policy-chunk-001"
    assert chunks[1].metadata["start_char"] < chunks[1].metadata["end_char"]
