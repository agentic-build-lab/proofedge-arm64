# ProofEdge v1.0.0 — Challenge Release

ProofEdge is an evidence-gated, local-first migration-assurance agent built for the Cloud AI track
of the Arm Create: AI Optimization Challenge.

## Highlights

- Bounded, non-executing source/target repository analysis.
- Deterministic contract, claim, coverage, and evidence gates.
- Strict local `llama.cpp` planning with explicit fallback behavior.
- Prompt-injection neutralization and loopback-only inference hardening.
- Frozen deterministic and local-model quality controls.
- Independent native Neoverse N2 confirmation: +0.5604% pp1024 and +4.2808% tg128 with KleidiAI,
  while both runtimes passed all frozen optimized-context quality cases.
- Public demo, complete raw evidence, launch film source, threat model, and reproducibility guide.

## Release assets

The release includes a source archive, a rendered 1080p challenge video, the complete native Arm64
confirmation evidence bundle, and a SHA-256 checksum manifest. No model weights or runtime binaries
are redistributed.

## Evidence boundary

The throughput comparison keeps model bytes, quantization, source, VM, workload, and threads
constant. It is not an end-to-end latency or energy claim. The first exploratory decode regression
remains public.
