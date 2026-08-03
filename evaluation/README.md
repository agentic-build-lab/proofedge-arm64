# Frozen Evaluation Corpus

This corpus prevents latency work from quietly eroding product usefulness. The fixtures and their
expected static categories were frozen before runtime optimization. The stricter model-evidence
oracles were frozen after the local-model path existed and before native profile tuning.

## Included cases

1. `python-refund-v2`: challenge-created, MIT-licensed Python migration with changed behavior, a
   changed signature, one unsupported completeness claim, and a prompt-injection canary.
2. `openapi-orders-v2`: challenge-created, MIT-licensed service-contract migration with a changed
   response status and missing target tests.
3. `qs-go-external.json`: metadata-only disclosure of separately published pre-existing work. It
   is not fetched, copied, or counted in the executable score.

The two executable cases are synthetic controls, not claims about defects in third-party
software. They are intentionally tiny so every expected finding and evidence anchor can be audited
by eye. Their perfect score must not be generalized into broad migration accuracy.

## Deterministic evaluation

```bash
proofedge evaluate --cases evaluation/cases --output evaluation/results/deterministic.json
```

Current result: 2/2 case passes, 5/5 expected categories, unsupported-claim recall 1.00, and false
unsupported-claim rate 0.00. These are deterministic static-check metrics, not model accuracy.

## Local-model evaluation

With a pinned loopback `llama-server` running:

```bash
proofedge evaluate-model \
  --cases evaluation/cases \
  --endpoint http://127.0.0.1:8080 \
  --profile optimized \
  --output evaluation/results/local-model.json
```

The evaluator checks strict schema completion, raw and published reference validity, objective
coverage, proposal density, canary leakage, and fallback. See the full
[evaluation protocol](../docs/EVALUATION.md).
