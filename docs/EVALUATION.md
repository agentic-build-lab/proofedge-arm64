# Evaluation Protocol

ProofEdge separates deterministic analyzer quality, local-model evidence quality, runtime
throughput, and end-to-end product latency. A number from one layer is never substituted for
another.

## Frozen corpus

Two challenge-created MIT-licensed controls are executable:

- `python-refund-v2` contains a rounding-policy change, loss of refund-reason behavior, a weak
  completeness claim, and a repository prompt injection.
- `openapi-orders-v2` changes an HTTP success status and removes detectable target tests.

`qs-go-external.json` is metadata about pre-existing work and is excluded from the current score.
The corpus is deliberately small enough to audit by eye. Its limits are disclosed; 2/2 does not
mean broad migration accuracy.

## Deterministic gate

Run:

```bash
proofedge evaluate --cases evaluation/cases --output evaluation/results/deterministic.json
```

Current result: 2/2 case passes, 5/5 category matches, category recall 1.00,
unsupported-claim recall 1.00, and false unsupported-claim rate 0.00.

Definitions:

- **Category recall:** matched predeclared risk categories divided by expected categories.
- **Unsupported-claim recall:** known unsupported manifest claims rejected by the analyzer divided
  by expected unsupported claims.
- **False unsupported-claim rate:** supported claims incorrectly rejected divided by all declared
  claims.

These are static-analyzer metrics, not language-model metrics.

## Frozen local-model gate

Each case has `model-golden.json` with source/target SHA-256 values, objective evidence ranges, and
forbidden injection canaries. File hashes and evidence anchors were frozen before native profile
tuning. Semantic requirements were added after an independent usefulness audit exposed that a
valid citation can still support a useless test; those requirements were then frozen before the
revision-2 confirmation.

The response must pass the strict schema before scoring. Per case it must also satisfy:

| Metric | Gate |
| --- | ---: |
| Schema completion | 1.00 |
| Raw reference validity | ≥ 0.75 |
| Risk-evidence coverage | ≥ 0.75 |
| Semantic objective coverage | ≥ 0.75 |
| Gold-target density | ≥ 0.40 |
| Canary leakage | 0 |
| Deterministic fallback | 0 |

- **Raw reference validity:** accepted proposals divided by all model proposals.
- **Published reference validity:** 1.00 only when at least one proposal survives; rejected
  proposals never enter the published test plan.
- **Risk-evidence coverage:** distinct predeclared objectives matched by accepted evidence divided
  by all objectives.
- **Semantic objective coverage:** objectives whose evidence, purpose, executable inputs, and
  source-versus-target relation all satisfy the frozen case requirement divided by all objectives.
- **Gold-target density:** objectives matched divided by accepted proposals, discouraging verbose
  but irrelevant output.

Matching uses deterministic maximum bipartite matching so one proposal cannot inflate several
objectives. A visible source/target difference is scored `investigate` unless explicit evidence
declares the change intentional. The quality workflow evaluates baseline and optimized context
profiles on both the baseline and KleidiAI runtime, producing four ledgers and preserving raw
responses and exits.

## Performance acceptance

Exploratory tuning may choose a profile; it may not establish the final claim. A confirmation run
must use the frozen model/runtime artifacts, a predeclared workload, same-host interleaving, raw
logs, and the quality gate above. No energy metric is reported without calibrated telemetry.

Independent run
[`30830782393`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30830782393)
passed this policy. Both baseline and KleidiAI optimized-context ledgers passed 2/2 cases with
schema completion 1.00, raw reference validity 1.00, risk-evidence coverage 1.00, zero canary
leakage, and zero fallback. The runtime A/B simultaneously measured +0.560% pp1024 and +4.281%
tg128 mean throughput for the preselected KleidiAI profile.

The two optimized-context ledgers also produced byte-identical response hashes across runtimes.
Their aggregate prompt-plus-generation compute decreased by 1.8693%. This timing is reported as
descriptive model compute inside the frozen product requests, not as user-observed TTFT or full
ProofEdge end-to-end latency.
