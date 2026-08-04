# Benchmarks

## Confirmed Arm64 result

ProofEdge's final claim comes from an independent confirmation of a profile selected in a
separate exploratory run. The model, quantization, `llama.cpp` commit, native VM, workload, and
thread count were identical; the causal build change was `GGML_CPU_KLEIDIAI=OFF` versus `ON`.

| Metric | Baseline | KleidiAI | Change |
| --- | ---: | ---: | ---: |
| Prompt processing, pp1024 | 96.7379 tok/s | 97.2800 tok/s | **+0.5604%** |
| Token generation, tg128 | 35.2443 tok/s | 36.7531 tok/s | **+4.2808%** |

Run [`30830782393`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30830782393)
used four fresh processes in ABBA order and seven observations per block on a native `aarch64`
Neoverse N2 GitHub runner. The selected profile was 4 threads, KleidiAI chunk multiplier 1,
batch 1024, and micro-batch 256. Logs confirmed runtime selection of the I8MM Q4 kernel.

Both baseline and KleidiAI also passed 2/2 frozen optimized-context model cases with schema
completion 1.00, raw-reference validity 1.00, risk-evidence coverage 1.00, zero canary leakage,
and zero fallback. See the
[machine-readable summary](benchmarks/results/gha-30830782393-summary.json) and
[complete raw bundle](benchmarks/raw/gha-30830782393).

## Honest evidence chain

The first ABBA profile was mixed: +0.5322% pp512 and −0.6967% tg128. It remains published in
[`benchmarks/results/gha-30822903168-summary.json`](benchmarks/results/gha-30822903168-summary.json).
Exploratory run
[`30828989800`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30828989800)
then selected a profile using predeclared rules. Only the later, separately launched run above is
used for the confirmed claim.

The bootstrap ranges in the summary resample observations within processes and are descriptive;
they are not confidence intervals across independent hosts. `llama-bench` is not end-to-end
product latency, and no energy claim is made. Full protocol, artifacts, and qualifications are in
[`benchmarks/README.md`](benchmarks/README.md).
