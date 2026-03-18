from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from project.rag.generate import REFUSAL_MESSAGE, extract_citations, generate_answer
from project.rag.models import PipelineResult, RetrievedChunk
from project.rag.retrieve import filter_retrieved_chunks, retrieve_chunks

AnswerGenerator = Callable[[str, list[RetrievedChunk]], str]


def append_event(log_path: Path, payload: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def refuse(
    question: str,
    retrieved_chunks: list[RetrievedChunk],
    reason: str,
    log_path: Path,
) -> PipelineResult:
    event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "question": question,
        "refused": True,
        "reason": reason,
        "retrieved_chunks": [asdict(chunk) for chunk in retrieved_chunks],
    }
    append_event(log_path, event)
    return PipelineResult(
        question=question,
        answer=REFUSAL_MESSAGE,
        citations=[],
        retrieved_chunks=retrieved_chunks,
        refused=True,
        refusal_reason=reason,
    )


def answer_question(
    question: str,
    index_dir: Path,
    top_k: int = 3,
    score_threshold: float = 0.35,
    log_path: Path | None = None,
    generator: AnswerGenerator | None = None,
) -> PipelineResult:
    log_file = log_path or Path("artifacts/logs/rag_events.jsonl")
    retrieved = retrieve_chunks(question=question, index_dir=index_dir, top_k=top_k)
    filtered = filter_retrieved_chunks(retrieved, score_threshold=score_threshold)

    if not retrieved:
        return refuse(
            question=question,
            retrieved_chunks=[],
            reason="no_retrieval_results",
            log_path=log_file,
        )
    if not filtered:
        return refuse(
            question=question,
            retrieved_chunks=retrieved,
            reason="all_results_below_threshold",
            log_path=log_file,
        )
    if filtered[0].score < score_threshold:
        return refuse(
            question=question,
            retrieved_chunks=retrieved,
            reason="top_score_below_threshold",
            log_path=log_file,
        )

    answer_generator = generator or generate_answer
    answer = answer_generator(question, filtered)
    citations = extract_citations(answer)
    return PipelineResult(
        question=question,
        answer=answer,
        citations=citations,
        retrieved_chunks=retrieved,
        refused=answer.strip() == REFUSAL_MESSAGE,
        refusal_reason="model_refusal" if answer.strip() == REFUSAL_MESSAGE else None,
    )
