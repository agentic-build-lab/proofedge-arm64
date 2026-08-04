# Evaluation

ProofEdge evaluates four layers independently so a throughput result cannot substitute for model
quality or product correctness.

| Layer | Frozen check | Current result |
| --- | --- | --- |
| Deterministic analyzer | Two challenge-created migration controls | 2/2 cases; 5/5 categories; unsupported-claim recall 1.00; false unsupported rate 0.00 |
| Local-model evidence | Strict schema, reference validity, predeclared risk objectives, injection canaries, fallback | Baseline and KleidiAI each pass 2/2 optimized-context cases; schema/reference/coverage 1.00; canary and fallback 0 |
| Runtime throughput | Same model/runtime workload, native Arm64 ABBA | +0.5604% pp1024 and +4.2808% tg128 for the confirmed KleidiAI profile |
| Product-request model compute | Prompt + generation timings inside two frozen quality requests | 13.367 → 13.118 s mean (−1.869%); byte-identical response hashes; descriptive n=2 |
| Deterministic function latency | Direct static evaluation of both frozen cases | Latest-main native warm p50 2.397 ms and p95 2.539 ms; excludes interpreter/CLI startup, report I/O, and local-model inference |

The corpus is intentionally small and auditable; 2/2 is not a claim of broad migration accuracy.
Model objectives and thresholds were frozen before the selected profile's confirmation run.
Matching is deterministic, and unsupported or malformed model proposals are excluded from the
published ledger rather than repaired silently.

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
[`benchmarks/raw/gha-30830782393/quality`](benchmarks/raw/gha-30830782393/quality).
