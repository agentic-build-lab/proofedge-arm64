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

The raw response must pass the strict schema before use. It is retained in every ledger but does
not directly become a published test. The model ranks risks detected from the repository; a
deterministic AST/OpenAPI compiler instantiates at most two tests with executable inputs, an
explicit source-versus-target purpose, and a visible citation. Its provenance states whether each
selection was model-aligned or supplied by the safety floor. Both raw and compiled response
hashes are retained, and injection canaries are checked across both forms.

The compiled response is scored against the unchanged frozen semantic objectives. Revision 3
introduces the separate, stricter compiled-reference threshold below; per case it must satisfy:

| Metric | Gate |
| --- | ---: |
| Schema completion | 1.00 |
| Raw model reference validity | Reported; does not authorize publication |
| Compiled reference validity | 1.00 |
| Risk-evidence coverage | ≥ 0.75 |
| Semantic objective coverage | ≥ 0.75 |
| Gold-target density | ≥ 0.40 |
| Canary leakage | 0 |
| Deterministic fallback | 0 |

- **Raw model reference validity:** raw proposals with valid visible citations divided by all raw
  proposals. It preserves the original metric meaning and is diagnostic in revision 3 because raw
  model wording has no direct publication authority.
- **Compiled reference validity:** accepted compiled proposals divided by all compiled proposals;
  revision 3 requires 1.00.
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
responses, compiled responses, compiler provenance, and exits.

## Performance acceptance

Exploratory tuning may choose a profile; it may not establish the final claim. A confirmation run
must use the frozen model/runtime artifacts, a predeclared workload, same-host interleaving, raw
logs, and the quality gate above. No energy metric is reported without calibrated telemetry.

Final run
[`30880259094`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30880259094)
passed this policy at revision 3. All four baseline/optimized × KleidiAI-off/on ledgers passed 2/2
cases with schema completion, compiled-reference validity, semantic-objective coverage, and
risk-evidence coverage all 1.00, plus zero canary leakage and zero fallback. Raw-model reference
validity remains separately disclosed at 0.50 for the baseline build and 0.75 for KleidiAI. The
same-workload runtime A/B measured +0.6029% pp1024 and +6.3783% tg128 mean throughput.

Five complete two-case product trials per build all passed. Published compiled-plan hashes were
stable and identical across builds. Client-observed task p50 changed from 45.387 to 44.639 seconds,
and request TTFT p50 from 14.960 to 14.867 seconds. Raw model responses and completion token counts
differed across builds, so exact model-compute comparison is ineligible and the end-to-end changes
are descriptive product observations, not isolated kernel effects.
