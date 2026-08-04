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
context depth under rules committed before results were inspected. Final native run `30880259094`
measured +0.6029% pp1024 and +6.3783% tg128 in a four-process ABBA design, with the runtime log
proving I8MM Q4 kernel selection. All four local-model quality configurations passed 2/2 frozen
cases under the semantic and compiled-reference gates.

The same run repeated the complete two-case product task five times per build. Every trial passed
and compiled published-plan hashes were identical across builds. Task p50 changed from 45.387 to
44.639 seconds and streamed TTFT p50 from 14.960 to 14.867 seconds. Raw model outputs and
completion token counts differed, so these are descriptive product observations and exact model
compute comparison is explicitly ineligible.

This is deliberately a narrow throughput claim. ProofEdge does not relabel `llama-bench` as
end-to-end latency, does not infer quality from identical model bytes, and does not report energy
without calibrated power telemetry. Full design and causal boundaries are documented in
[`docs/OPTIMIZATION.md`](docs/OPTIMIZATION.md).
