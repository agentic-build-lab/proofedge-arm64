# Decision Log

## 2026-08-03 — Select the Cloud AI track

**Status:** Accepted, pending final rules reconciliation.

The official track page explicitly includes Arm64 cloud inference, CPU-optimized frameworks,
`llama.cpp`, KleidiAI, and agentic workloads. ProofEdge naturally fits this scope and can be
benchmarked on reproducible native Arm64 cloud runners without requiring proprietary hardware.

## 2026-08-03 — Separate model, runtime, and workflow optimizations

**Status:** Accepted.

The benchmark suite will not present a model or quantization change as an Arm-specific speedup.
It will publish three layers:

1. runtime: baseline `llama.cpp` versus KleidiAI-enabled `llama.cpp`, same model artifact;
2. serving: threads, batch size, memory mapping, cache, and context settings;
3. workflow: evidence retrieval, context compression, staged routing, and constrained output.

Each layer must preserve the fixed evaluation quality budget.

## 2026-08-03 — Make deterministic mode a first-class product path

**Status:** Accepted.

Judges and contributors must be able to reproduce useful behavior without credentials or a
model download. Deterministic mode will scan contracts, compare surfaces, validate evidence,
and render the same report schema used by the local-model path. It is a fallback and evaluation
oracle, not a fabricated inference benchmark.

## 2026-08-03 — Treat repositories as hostile input

**Status:** Accepted.

ProofEdge will never execute repository code during analysis by default. It will bound file
size, total bytes, symlink traversal, subprocess commands, output volume, and time. Repository
content is evidence, never instruction.

