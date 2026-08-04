# ProofEdge v1.0.1 — Semantic Evidence Release

This release hardens the challenge entry after an independent public-artifact and model-usefulness
audit.

## Highlights

- Replaces citation-only model scoring with semantic objective validation for purpose, executable
  inputs, and source-versus-target relation.
- Constrains the compact model to rank mechanically detected risks; a deterministic AST/OpenAPI
  compiler authors the citable, executable published plan and records model-aligned versus
  safety-floor provenance.
- Preserves four failed semantic canaries and excludes every attractive throughput result whose
  quality gate failed.
- Adds repeated full-task latency, client-observed streaming TTFT, server startup, CPU, RSS, model
  size, and fixed-corpus quality evidence on native Arm64.
- Publishes final native run `30880259094`: +0.6029% pp1024 and +6.3783% tg128 in same-host ABBA,
  with all four quality configurations passing 2/2 cases and all repeated product trials passing.
- Marks exact model-compute comparison ineligible when raw responses or completion token counts
  differ, while separately reporting identical compiled published-plan hashes.
- Writes an explicit deterministic fallback ledger when the local server is unavailable.
- Bounds and validates migration manifests, including path traversal, count, size, line, and hash
  controls.
- Self-hosts the public demo fonts so production HTML contains no build-machine path.
- Includes the patched demo dependency state with zero production audit findings.
- Records the embedded video sound-effect provenance and license boundary.

The complete native evidence, environment metadata, hashes, and failed-run history are linked from
[`BENCHMARKS.md`](../BENCHMARKS.md). ProofEdge remains MIT licensed.
