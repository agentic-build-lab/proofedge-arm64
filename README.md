# ProofEdge

**Evidence before confidence. Private migration assurance on Arm64.**

ProofEdge is a local-first AI engineering agent that compares a source system with its
migrated implementation, builds a differential-testing plan, and emits an auditable evidence
ledger. It is designed for compact-model inference on CPU-only Arm64 infrastructure so that
private source code does not need to leave the machine.

This project is being built for the **Arm Create: AI Optimization Challenge**, Cloud AI track.
Benchmark claims remain explicitly provisional until repeated measurements on genuine Arm64
hardware and quality-gate results are published.

## The problem

AI can translate code quickly. It cannot, by fluency alone, prove that a migration preserved
behavior. Reviewers need a concrete answer to four questions:

1. Which contracts must remain true?
2. What changed, and where is the evidence?
3. Which tests would distinguish the old and new behavior?
4. Which claims are unsupported by reproducible artifacts?

ProofEdge turns those questions into a bounded, inspectable workflow instead of a chat log.

## Planned evidence path

- Compare a baseline and a KleidiAI-enabled `llama.cpp` build using the same model,
  quantization, prompts, task set, and native Arm64 machine class.
- Isolate application-level optimizations: context selection, staged inference, structured
  output constraints, caching, thread count, and batch/context tuning.
- Publish every trial, including cold and warm starts, environment metadata, and failed runs.
- Reject an optimization if fixed-set task success or unsupported-claim rate regresses beyond
  the documented quality budget.

## Current status

The repository is at the architecture/scaffolding stage. The deterministic engine, local model
adapter, golden corpus, benchmark harness, user interface, and real-Arm results will land as
separate reviewable commits.

## License

[MIT](LICENSE)

