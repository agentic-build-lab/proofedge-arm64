# Optimization

ProofEdge optimizes a local, CPU-only Arm64 inference path while keeping the model fixed. The
measured build-level change enables KleidiAI in a pinned `llama.cpp` commit; serving parameters
are selected separately, and repository-context reduction is treated as a distinct workflow
layer.

## Final selected profile

- Native target: Neoverse N2, 4 vCPU, `aarch64`
- Model: Qwen2.5-Coder-1.5B-Instruct Q4_0, identical bytes in both arms
- Runtime: `llama.cpp` commit `67d5978bb1ba490070ddbd2a7c59c7ec5a60b7cc`
- Threads: 4
- `GGML_KLEIDIAI_CHUNK_MULTIPLIER`: 1
- Batch / micro-batch: 1024 / 256
- CPU only; no GPU offload

The selection run searched thread count, KleidiAI chunk multiplier, batch, micro-batch, and
context depth under rules committed before results were inspected. The independent confirmation
then measured +0.5604% pp1024 and +4.2808% tg128 with the runtime log proving I8MM Q4 kernel
selection. Both runtimes independently passed the frozen local-model evidence gate.

The same confirmation ledgers contain the prompt and generation timings for two complete frozen
quality requests. With identical context, token counts, and response hashes, aggregate model
compute decreased by 1.8693% (26.7348 to 26.2351 seconds). This is a descriptive n=2 bridge from
the runtime microbenchmark to the product workload; it is not full CLI latency and is not used as
a repeated-trial estimate.

This is deliberately a narrow throughput claim. ProofEdge does not relabel `llama-bench` as
end-to-end latency, does not infer quality from identical model bytes, and does not report energy
without calibrated power telemetry. Full design and causal boundaries are documented in
[`docs/OPTIMIZATION.md`](docs/OPTIMIZATION.md).
