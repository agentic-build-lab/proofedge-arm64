# Evaluation

ProofEdge evaluates four layers independently so a throughput result cannot substitute for model
quality or product correctness.

| Layer | Frozen check | Current result |
| --- | --- | --- |
| Deterministic analyzer | Two challenge-created migration controls | 2/2 cases; 5/5 categories; unsupported-claim recall 1.00; false unsupported rate 0.00 |
| Local-model evidence | Strict schema, compiled-reference validity, predeclared risk objectives, injection canaries, fallback | Four configurations pass 2/2 cases; compiled references, semantics, and risk coverage 1.00; canary and fallback 0 |
| Runtime throughput | Same model/runtime workload, native Arm64 ABBA | +0.6029% pp1024 and +6.3783% tg128 in final run `30880259094` |
| Repeated product task | Five complete two-case trials and ten streamed requests per build | Task p50 45.387 → 44.639 s; TTFT p50 14.960 → 14.867 s; all runs passed; descriptive because raw outputs differed |
| Deterministic function latency | Direct static evaluation of both frozen cases | Main run `30882095544`: 30/30 passes, warm p50 2.357 ms and p95 2.419 ms; excludes interpreter/CLI startup, report I/O, and local-model inference |

The corpus is intentionally small and auditable; 2/2 is not a claim of broad migration accuracy.
Model objectives were frozen before the selected profile's confirmation run. Gate revisions and
their pre-run freeze points are retained in the benchmark history.
Matching is deterministic. Raw model proposals are retained separately; a disclosed AST/OpenAPI
compiler turns model-ranked changes into citable test specifications and marks safety-floor
selections explicitly. Unsupported raw wording is never silently relabeled as model-authored
evidence. Revision 3 reports raw-model reference validity under its original definition and gates
publication separately on compiled reference validity 1.00.

Run the credential-free gate with:

```bash
proofedge evaluate --cases evaluation/cases --output evaluation/results/deterministic.json
```

With a pinned loopback `llama-server`, run the model gate with:

```bash
proofedge evaluate-model \
  --cases evaluation/cases \
  --endpoint http://127.0.0.1:8080 \
  --profile optimized \
  --output evaluation/results/local-model.json
```

Definitions, thresholds, corpus details, and the performance acceptance policy are in
[`docs/EVALUATION.md`](docs/EVALUATION.md). The final native ledgers are under
[`benchmarks/raw/gha-30880259094/quality`](benchmarks/raw/gha-30880259094/quality).
