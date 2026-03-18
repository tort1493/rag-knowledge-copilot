from pathlib import Path

from project.rag.generate import REFUSAL_MESSAGE, answer_has_citations
from project.rag.models import RetrievedChunk
from project.rag.pipeline import answer_question


def test_refusal_when_retrieval_empty(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("project.rag.pipeline.retrieve_chunks", lambda **_: [])

    result = answer_question(
        question="Unsupported question",
        index_dir=tmp_path,
        top_k=3,
        score_threshold=0.35,
        log_path=tmp_path / "events.jsonl",
    )

    assert result.refused is True
    assert result.answer == REFUSAL_MESSAGE
    assert result.refusal_reason == "no_retrieval_results"


def test_refusal_when_scores_below_threshold(monkeypatch, tmp_path: Path) -> None:
    low_score_chunks = [
        RetrievedChunk(
            chunk_id="doc-chunk-000",
            source_file="doc.md",
            text="Some text",
            score=0.10,
            metadata={"source_file": "doc.md", "chunk_id": "doc-chunk-000"},
        )
    ]
    monkeypatch.setattr("project.rag.pipeline.retrieve_chunks", lambda **_: low_score_chunks)

    result = answer_question(
        question="Weakly supported question",
        index_dir=tmp_path,
        top_k=3,
        score_threshold=0.35,
        log_path=tmp_path / "events.jsonl",
    )

    assert result.refused is True
    assert result.answer == REFUSAL_MESSAGE
    assert result.refusal_reason == "all_results_below_threshold"


def test_citation_format_detected() -> None:
    answer = "Support hours are Monday through Friday, 8:00 AM to 6:00 PM Eastern Time. [support_policy.md:support_policy-chunk-000]"
    assert answer_has_citations(answer) is True
