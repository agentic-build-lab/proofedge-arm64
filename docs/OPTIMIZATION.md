# Arm64 Optimization Strategy

## Causal layers

ProofEdge keeps three optimization layers independent:

1. **Runtime:** same `llama.cpp` commit and Q4_0 model with `GGML_CPU_KLEIDIAI=OFF` versus `ON`.
2. **Serving:** thread count, KleidiAI chunk multiplier, batch, micro-batch, and context depth.
3. **Workflow:** whole scanned context versus evidence-selected numbered context, with the same
   model and runtime.

Quantization and model swaps are not labeled Arm optimizations. `llama-bench` results are not
labeled end-to-end latency because they exclude tokenization, structured parsing, evidence gates,
reporting, and some sampling work.

## Pinned runtime comparison

- Native runner: GitHub `ubuntu-24.04-arm`, reported as `aarch64`, Neoverse N2, 4 vCPU
- `llama.cpp`: `67d5978bb1ba490070ddbd2a7c59c7ec5a60b7cc`
- Model: Qwen2.5-Coder-1.5B-Instruct Q4_0
- Model SHA-256: `aa8353e0d0fca3a0041828701e90db7635197400f040676d11d7798665fa316e`
- Fixed workload: pp512 + tg128, 4 threads, batch 2048, micro-batch 512, CPU only
- Order: baseline, KleidiAI, KleidiAI, baseline; 5 repetitions per block

The only causal build change is `GGML_CPU_KLEIDIAI`. Build caches, binary hashes, CMake caches,
`ldd`, environment facts, raw JSON, stderr, and `/usr/bin/time -v` are preserved.

## First result

| Metric | Baseline | KleidiAI | Mean change |
| --- | ---: | ---: | ---: |
| Prompt processing | 130.4856 tok/s | 131.1800 tok/s | +0.5322% |
| Token generation | 35.38354 tok/s | 35.13702 tok/s | −0.6967% |

Interpretation: mixed/negative. The exploratory within-process bootstrap for prefill is positive,
while the decode interval crosses zero and the mean regresses. This is one VM and one profile, so
it is neither an independent confidence interval nor an end-to-end win.

## Frozen exploratory tuning

The predeclared `arm64-tuning-v1.json` sweep tests:

- threads 2, 3, 4 × KleidiAI chunk multiplier 1, 2, 4, 8;
- stage-one selection: highest tg128 among candidates within 2% of best pp512, then lower RSS,
  fewer threads, lower chunk;
- batch/micro-batch pairs 512/128, 1024/256, 2048/512 at pp1024;
- decode at context depths 0, 512, and 1024.

This selects an exploratory profile only. The profile must then survive a distinct confirmation
run and the frozen local-model gate. The runtime log must show a compatible KleidiAI Q4 kernel;
build-time enablement alone is insufficient evidence.

Exploratory run
[`30828989800`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30828989800)
selected 4 threads, chunk multiplier 1, batch 1024, and micro-batch 256. At stage one, the selected
candidate measured pp512 131.680 tok/s and tg128 36.566 tok/s. At stage two, the selected pair
measured pp1024 97.078 tok/s. These are selection data, not confirmation claims. The independent
profile and acceptance policy are frozen in `benchmarks/config/arm64-confirm-v1.json`.

## Independent confirmation result

Run
[`30830782393`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30830782393)
used the committed selection without further tuning: 4 threads, chunk multiplier 1, batch 1024,
micro-batch 256, pp1024, and tg128. Four new benchmark processes ran in ABBA order with seven
observations per block.

| Metric | Baseline | KleidiAI | Mean change |
| --- | ---: | ---: | ---: |
| Prompt processing | 96.7379 tok/s | 97.2800 tok/s | **+0.5604%** |
| Token generation | 35.2443 tok/s | 36.7531 tok/s | **+4.2808%** |

The optimized runtime selected the I8MM Q4 kernel at runtime. Baseline and KleidiAI each passed
2/2 frozen optimized-context model-quality cases with perfect schema completion, reference
validity, and risk coverage, plus zero canary leakage and zero fallback. This supports a narrow,
reproducible same-model runtime-throughput claim; it does not support an energy or end-to-end
latency claim.

Those same ledgers recorded prompt and generation timings for two complete optimized-context
quality requests. Both configurations saw identical context hashes, prompt/completion token
counts, and response hashes. Aggregate model compute decreased from 26.7348 to 26.2351 seconds
(**−1.8693%**), with per-case changes of −2.3286% and −1.4807%. Because each case was captured
once and server timings exclude non-model product stages, this is descriptive product-task
evidence rather than a repeated full end-to-end claim. The derivation is reproducible in
`benchmarks/results/gha-30830782393-product-quality-summary.json`.

## Workflow optimization boundary

The current fixtures produce only modest context reduction, including one case with no reduction.
Therefore ProofEdge does not claim a workflow latency or context-compression win from these cases.
A future claim requires larger frozen fixtures and streaming server timing that measures first
token directly; non-streaming CLI latency will not be relabeled as TTFT.
