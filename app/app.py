from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from project.rag.generate import REFUSAL_MESSAGE
from project.rag.index import build_index
from project.rag.pipeline import answer_question

load_dotenv(ROOT / ".env")

INDEX_DIR = ROOT / "artifacts" / "index"
KNOWLEDGE_BASE_DIR = ROOT / "data" / "knowledge_base"
BUILD_INFO_PATH = INDEX_DIR / "build_info.json"


def read_build_info() -> dict[str, str] | None:
    if not BUILD_INFO_PATH.exists():
        return None
    return json.loads(BUILD_INFO_PATH.read_text(encoding="utf-8"))


def render_status() -> None:
    build_info = read_build_info()
    index_found = BUILD_INFO_PATH.exists()
    with st.sidebar:
        st.subheader("Index Status")
        st.write(f"Index found: {'Yes' if index_found else 'No'}")
        st.write(f"Last built: {build_info['last_built'] if build_info else 'Not available'}")
        if build_info:
            st.write(f"Documents: {build_info['documents']}")
            st.write(f"Chunks: {build_info['chunks']}")


def trigger_rebuild() -> None:
    summary = build_index(knowledge_base_dir=KNOWLEDGE_BASE_DIR, index_dir=INDEX_DIR)
    build_info = {
        "last_built": datetime.now(UTC).isoformat(),
        "documents": summary["documents"],
        "chunks": summary["chunks"],
    }
    BUILD_INFO_PATH.write_text(json.dumps(build_info, indent=2), encoding="utf-8")


def main() -> None:
    st.set_page_config(page_title="RAG Knowledge Copilot", layout="wide")
    st.title("RAG Knowledge Copilot with Guardrails")
    st.caption("Answers only from the local synthetic handbook, cites sources, and refuses when retrieval is weak.")

    with st.sidebar:
        st.subheader("Controls")
        top_k = st.slider("top_k", min_value=1, max_value=5, value=3)
        threshold = st.slider("score threshold", min_value=0.0, max_value=1.0, value=0.35, step=0.05)
        if st.button("Rebuild index", use_container_width=True):
            with st.spinner("Building persistent index..."):
                try:
                    trigger_rebuild()
                    st.success("Index rebuilt successfully.")
                except Exception as exc:
                    st.error(f"Index rebuild failed: {exc}")
        render_status()

    question = st.text_area(
        "Ask a question about the handbook",
        placeholder="Example: When does a customer qualify for a refund?",
        height=120,
    )

    if st.button("Submit", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Enter a question to continue.")
            return
        try:
            result = answer_question(
                question=question.strip(),
                index_dir=INDEX_DIR,
                top_k=top_k,
                score_threshold=threshold,
                log_path=ROOT / "artifacts" / "logs" / "rag_events.jsonl",
            )
        except Exception as exc:
            st.error(f"Question failed: {exc}")
            return

        st.subheader("Answer")
        if result.answer == REFUSAL_MESSAGE:
            st.warning(result.answer)
        else:
            st.markdown(result.answer)

        if result.citations:
            st.caption("Citations: " + ", ".join(result.citations))

        st.subheader("Retrieved Chunks")
        if not result.retrieved_chunks:
            st.info("No chunks were retrieved.")
        for chunk in result.retrieved_chunks:
            title = f"{chunk.source_file} | {chunk.chunk_id} | score={chunk.score:.3f}"
            with st.expander(title):
                st.json(chunk.metadata)
                st.code(chunk.text, language="markdown")


if __name__ == "__main__":
    main()
