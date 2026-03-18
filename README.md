# RAG Knowledge Copilot with Guardrails

This project is a local-first RAG demo that answers questions only from a synthetic knowledge base, cites its sources, and refuses when grounded support is weak or missing.

## Features

- Local markdown knowledge base under `data/knowledge_base/`
- Persistent Chroma index under `artifacts/index/`
- Streamlit UI with retrieval inspection and rebuild controls
- Deterministic refusal guardrail and logged refusal reasons
- Offline mini-evaluation harness with summary metrics
- Lightweight pytest coverage for chunking, refusal, and citation formatting

## Quickstart

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set your API key:

```bash
cp .env.example .env
```

Add `OPENAI_API_KEY` to `.env` or export it in your shell.

4. Build the index:

```bash
python scripts/build_index.py
```

5. Launch the UI:

```bash
python -m streamlit run app/app.py
```

6. Run the offline evaluation:

```bash
python scripts/eval_rag.py
```

7. Run tests:

```bash
python -m pytest
```

## How the guardrails work

- Retrieval must return at least one chunk at or above the configured threshold.
- If retrieval is weak or empty, the assistant returns:

`I don't have enough information in the provided documents to answer that.`

- Retrieved documents are treated as untrusted data. The generation prompt explicitly rejects any instructions found inside retrieved text.
- Answerable responses must include inline citations in the format `[source_file.md:chunk_id]`.

## Project layout

- `app/app.py`: Streamlit demo UI
- `src/project/rag/`: chunking, indexing, retrieval, generation, pipeline
- `scripts/build_index.py`: builds the persistent index
- `scripts/eval_rag.py`: runs the offline mini-eval
- `eval/questions.json`: answerable and unanswerable evaluation set
- `docs/`: architecture, evaluation report, and runbook artifacts

## Screenshots

- `docs/screenshots/app-main.png` (placeholder)
- `docs/screenshots/app-retrieval-details.png` (placeholder)
