from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

load_dotenv(ROOT / ".env")

from project.rag.generate import REFUSAL_MESSAGE
from project.rag.pipeline import answer_question

CITATION_PATTERN = re.compile(r"\[[A-Za-z0-9_.-]+:[A-Za-z0-9_.-]+\]")


def load_questions(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_item(item: dict, index_dir: Path) -> dict:
    result = answer_question(
        question=item["question"],
        index_dir=index_dir,
        top_k=3,
        score_threshold=0.35,
        log_path=ROOT / "artifacts" / "logs" / "rag_events.jsonl",
    )
    answer_text = result.answer
    refused = answer_text.strip() == REFUSAL_MESSAGE
    has_citations = bool(CITATION_PATTERN.findall(answer_text))
    sources_used = sorted({chunk.source_file for chunk in result.retrieved_chunks[:3]})
    expected_sources = item.get("expected_sources", [])
    citation_coverage = (
        1.0
        if not expected_sources
        else len(set(expected_sources) & set(sources_used)) / len(expected_sources)
    )
    passed = True
    failure_reasons: list[str] = []

    if item["answerable"] and refused:
        passed = False
        failure_reasons.append("answerable_question_refused")
    if not item["answerable"] and not refused:
        passed = False
        failure_reasons.append("unanswerable_question_not_refused")
    if item["answerable"] and not has_citations:
        passed = False
        failure_reasons.append("missing_citations")
    if item["answerable"] and expected_sources and citation_coverage == 0:
        passed = False
        failure_reasons.append("expected_source_not_retrieved")

    return {
        "id": item["id"],
        "question": item["question"],
        "answerable": item["answerable"],
        "answer": answer_text,
        "refused": refused,
        "has_citations": has_citations,
        "expected_sources": expected_sources,
        "sources_used": sources_used,
        "citation_coverage": citation_coverage,
        "passed": passed,
        "failure_reasons": failure_reasons,
        "notes": item.get("notes", ""),
    }


def print_summary(results: list[dict]) -> None:
    total = len(results)
    answerable_items = [item for item in results if item["answerable"]]
    unanswerable_items = [item for item in results if not item["answerable"]]
    answerable_correct = sum(
        1 for item in answerable_items if item["passed"] and not item["refused"]
    )
    refusal_correct = sum(
        1 for item in unanswerable_items if item["passed"] and item["refused"]
    )
    citation_coverage = sum(item["citation_coverage"] for item in answerable_items) / max(
        1, len(answerable_items)
    )
    failures = [item for item in results if not item["passed"]]

    print("RAG Evaluation Summary")
    print("======================")
    print(f"Total questions: {total}")
    print(f"Answerable accuracy: {answerable_correct}/{len(answerable_items)}")
    print(f"Refusal correctness: {refusal_correct}/{len(unanswerable_items)}")
    print(f"Citation coverage %: {citation_coverage * 100:.1f}")
    print(f"Failures: {len(failures)}")
    if failures:
        print("\nFailure details:")
        for item in failures:
            reasons = ", ".join(item["failure_reasons"])
            print(f"- {item['id']}: {reasons} :: {item['question']}")


def main() -> None:
    questions = load_questions(ROOT / "eval" / "questions.json")
    index_dir = ROOT / "artifacts" / "index"
    results = [evaluate_item(item, index_dir=index_dir) for item in questions]
    output_dir = ROOT / "artifacts" / "eval"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "results.json"
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print_summary(results)
    print(f"\nWrote detailed results to {output_path}")


if __name__ == "__main__":
    main()
