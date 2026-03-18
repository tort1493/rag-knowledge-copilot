# Evaluation Report

## Scope

The MVP evaluation uses `eval/questions.json` with 25 offline prompts:

- 20 answerable or partially answerable policy questions drawn from the synthetic handbook
- 5 intentionally unsupported questions that should trigger refusal

## Metrics

`scripts/eval_rag.py` reports four headline metrics:

1. Answerable accuracy: answerable questions that are not refused and pass basic checks
2. Refusal correctness: unsupported questions that are explicitly refused
3. Citation coverage %: fraction of expected sources retrieved for answerable questions
4. Failure list: question IDs with concrete failure reasons

## Known failure modes

- False refusal when threshold is set too high relative to embedding distance distribution
- Weak citation coverage when the right document is semantically near the question but not in the top `k`
- Citation presence without perfect sentence-level attribution because the MVP validates format rather than every claim boundary
- Model paraphrase drift if retrieval is marginal but still above threshold

## Red-team cases included

- Unsupported organizational questions such as CEO identity
- Unsupported operational specifics such as production region and SOC 2 report date
- Questions that could invite hallucination because they sound plausible inside a handbook context

## Guardrail expectations

- User attempts to override system behavior should fail because the system prompt instructs the model to ignore such instructions.
- Retrieved prompt injection should fail because retrieved text is treated as untrusted and used only as evidence, not instructions.
- Unsupported content should produce the exact refusal string so downstream logging and eval remain deterministic.

## How to refresh the report

1. Rebuild the index: `python scripts/build_index.py`
2. Run the eval: `python scripts/eval_rag.py`
3. Review `artifacts/eval/results.json`
4. Update this document with current metrics, notable failures, and any threshold adjustments

## Current status

The current validated run produced these results:

- Total questions: 25
- Answerable accuracy: 21/21
- Refusal correctness: 4/4
- Citation coverage: 100.0%
- Failures: 0

The evaluation output was written to `artifacts/eval/results.json`.

Observed outcome:

- The retrieval threshold and synthetic handbook coverage were sufficient to answer all supported prompts in the current offline set.
- Unsupported prompts were refused consistently with the deterministic refusal message.
- Citation formatting and source retrieval matched the expected eval checks across the full question set.
