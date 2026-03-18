from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    source_file: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    source_file: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineResult:
    question: str
    answer: str
    citations: list[str]
    retrieved_chunks: list[RetrievedChunk]
    refused: bool
    refusal_reason: str | None = None
