# Decision Log

## 2026-08-03 — Select the Cloud AI track

**Status:** Accepted after rules reconciliation.

The official track includes Arm64 cloud inference, CPU-optimized frameworks, `llama.cpp`,
KleidiAI, and agentic workloads. ProofEdge fits that scope and can be benchmarked on reproducible
native Arm64 cloud runners without proprietary hardware.

## 2026-08-03 — Separate model, runtime, and workflow optimizations

**Status:** Accepted.

The benchmark suite will not present a model or quantization change as an Arm-specific speedup.
It publishes three layers:

1. runtime: baseline `llama.cpp` versus KleidiAI-enabled `llama.cpp`, same model artifact;
2. serving: threads, batch size, memory mapping, cache, and context settings;
3. workflow: evidence retrieval, context selection, staged routing, and constrained output.

Each layer must preserve the frozen evaluation quality budget.

## 2026-08-03 — Make deterministic mode a first-class product path

**Status:** Accepted.

Judges and contributors must be able to reproduce useful behavior without credentials or a model
download. Deterministic mode scans contracts, compares surfaces, validates evidence, and renders
the same report schema used by the local-model path. It is a fallback and evaluation oracle, not a
fabricated inference benchmark.

## 2026-08-03 — Treat repositories as hostile input

**Status:** Accepted.

ProofEdge does not execute repository code during analysis. It bounds file size, total bytes,
visited entries, file count, path length, directory depth, network response size, and model-output
shape. Repository content is evidence, never instruction.

## 2026-08-03 — Publish a mixed result instead of selecting a flattering metric

**Status:** Accepted.

The first same-host run improved mean prefill by 0.532% and regressed mean decode by 0.697%.
ProofEdge preserves both numbers and labels the run mixed/negative. A parameter sweep is
exploratory; any selected profile must be checked in a separate confirmation run with the frozen
model-quality gate.

## 2026-08-03 — Fail closed at the model boundary

**Status:** Accepted.

Model output must satisfy a closed schema and cite an existing line that appeared in its exact
context. Invalid proposals are recorded separately from unsupported migration claims. If no
proposal survives, the CLI reports deterministic fallback and returns a nonzero status.
