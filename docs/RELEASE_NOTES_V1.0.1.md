# ProofEdge v1.0.1 — Semantic Evidence Release

This release hardens the challenge entry after an independent public-artifact and model-usefulness
audit.

## Highlights

- Replaces citation-only model scoring with semantic objective validation for purpose, executable
  inputs, and source-versus-target relation.
- Preserves the first failed revision-2 native canary and excludes its attractive throughput
  result from the winning claim because quality failed.
- Adds repeated full-task latency, client-observed streaming TTFT, server startup, CPU, RSS, model
  size, and fixed-corpus quality evidence on native Arm64.
- Writes an explicit deterministic fallback ledger when the local server is unavailable.
- Bounds and validates migration manifests, including path traversal, count, size, line, and hash
  controls.
- Self-hosts the public demo fonts so production HTML contains no build-machine path.
- Includes the patched demo dependency state with zero production audit findings.
- Records the embedded video sound-effect provenance and license boundary.

The complete native evidence, environment metadata, hashes, and failed-run history are linked from
[`BENCHMARKS.md`](../BENCHMARKS.md). ProofEdge remains MIT licensed.
