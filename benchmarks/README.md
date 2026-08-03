# Native Arm64 Benchmark Evidence

ProofEdge separates claims that are often conflated:

1. **Runtime A/B:** same Q4_0 model and `llama.cpp` commit, built with
   `GGML_CPU_KLEIDIAI=OFF` and `ON` on one native Arm64 VM.
2. **Serving configuration:** fixed runtime with predeclared settings changed in an exploratory
   sweep.
3. **Workflow optimization:** whole scanned context versus evidence-selected context, with the
   same model and runtime.
4. **Composite product result:** only after runtime, serving, workflow, and quality evidence all
   pass their gates.

## First completed same-host A/B

GitHub Actions run
[`30822903168`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30822903168)
ran on native `aarch64` Neoverse N2 hardware in ABBA order. The source, model, quantization,
threads, batch sizes, and workload were fixed; only `GGML_CPU_KLEIDIAI` changed.

| Metric | Baseline mean | KleidiAI mean | Relative change |
| --- | ---: | ---: | ---: |
| pp512 | 130.4856 tok/s | 131.1800 tok/s | +0.5322% |
| tg128 | 35.38354 tok/s | 35.13702 tok/s | −0.6967% |

The prefill exploratory sample bootstrap interval was +0.229% to +0.758%. The decode interval was
−1.664% to +0.236% and crosses zero. These intervals resample within-process observations; they
are not confidence intervals across independent hosts.

**Interpretation: mixed/negative.** The configuration does not support a decode or end-to-end
speedup claim. The complete machine-readable summary is
[`results/gha-30822903168-summary.json`](results/gha-30822903168-summary.json), and the raw bundle
is under [`raw/gha-30822903168`](raw/gha-30822903168).

## Protocol

The native runtime workflow uses an ABBA block order to reduce bias from host drift. Every block
retains `llama-bench` JSON, verbose stderr, `/usr/bin/time -v`, environment metadata, source/model
hashes, build logs, CMake caches, dynamic-link facts, and binary identities. QEMU, FVP, and other
emulators are never accepted as performance evidence.

The pinned model is the official Apache-2.0
[`Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF`](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF)
Q4_0 artifact. Q4_0 is deliberate because the measured `llama.cpp` KleidiAI path can select Arm
Q4 kernels, allowing a same-model causal comparison. Q4_K_M may be studied separately but will not
be presented as the result of this frozen experiment.

The workflow also starts baseline and KleidiAI `llama-server` processes one at a time with prompt
caching and continuous batching disabled. It runs all frozen model cases under both context
profiles, preserves responses, and requires runtime logs to prove KleidiAI Q4 kernel selection.

## Exploratory tuning

[`config/arm64-tuning-v1.json`](config/arm64-tuning-v1.json) freezes the selection rules before
results are inspected. It searches threads and KleidiAI chunk multiplier first, then batch and
micro-batch pairs, and finally checks decode at multiple context depths. The chosen setting remains
exploratory until a separate confirmation benchmark passes the model-quality gate.

Run [`30828989800`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30828989800)
selected 4 threads, chunk multiplier 1, batch 1024, and micro-batch 256. The selection artifact
records pp512 131.680 tok/s, tg128 36.566 tok/s, and pp1024 97.078 tok/s for the relevant stages.
These values selected [`config/arm64-confirm-v1.json`](config/arm64-confirm-v1.json); they are not
reported as independent performance evidence.

## Qualifications

- The completed runtime evidence covers one native VM and one initial serving profile.
- `llama-bench` omits several end-to-end application stages.
- Peak RSS is a process measurement, not whole-host memory or energy.
- Energy is not reported because the hosted runner exposes no calibrated power telemetry.
- Model-quality equivalence cannot be inferred from identical model bytes; it has its own frozen
  evidence-objective gate.

See [optimization details](../docs/OPTIMIZATION.md), [evaluation](../docs/EVALUATION.md), and
[reproducibility](../docs/REPRODUCIBILITY.md).
