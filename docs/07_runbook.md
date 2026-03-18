# Runbook

## Purpose

Operate the RAG Knowledge Copilot demo safely, detect regression quickly, and define rollback triggers when grounding quality deteriorates.

## Normal operating procedure

1. Ensure `OPENAI_API_KEY` is present in the environment or `.env`.
2. Rebuild the index after any knowledge base changes:
   - `python scripts/build_index.py`
3. Launch the UI:
   - `streamlit run app/app.py`
4. Validate with a small smoke test:
   - ask one known answerable question
   - ask one known unanswerable question
   - confirm citations and refusal behavior

## Alerts and symptoms

- Frequent explicit refusals for known answerable questions
- Answers without citations
- Retrieval expanders showing empty results despite a built index
- Unsupported questions producing confident non-refusal answers
- Build failures caused by missing API key or embedding errors

## Rollback triggers

- Answerable accuracy drops materially in offline eval
- Refusal correctness drops below the expected baseline for unsupported questions
- Citation coverage falls to zero for multiple answerable prompts
- Users report grounded answers that cite irrelevant sources

## Incident steps

1. Stop using the current threshold or model settings for demos.
2. Re-run `python scripts/eval_rag.py` to confirm whether the issue is systematic.
3. Inspect `artifacts/logs/rag_events.jsonl` for refusal spikes or repeated failure patterns.
4. Rebuild the index to rule out stale or corrupted local state.
5. If the regression persists, revert the last retrieval, prompt, or knowledge base change.
6. Document the issue, affected prompts, and remediation in the retrospective notes.

## Recovery actions

- Lower the similarity threshold only if eval shows false refusals without materially harming refusal correctness.
- Increase `top_k` if the expected source is consistently just outside the returned set.
- Tighten prompt wording if answers start leaking unsupported claims.
- Rebuild the collection whenever source docs change or Chroma state looks inconsistent.

## Ownership

- Product/demo owner: repository maintainer
- Technical owner for retrieval quality: repository maintainer
- Incident reviewer: repository maintainer until a team structure exists
