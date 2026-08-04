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

## Product-task timing already present in the confirmation evidence

The quality ledgers also contain `llama-server` timings for the same two optimized-context
ProofEdge requests. Baseline and KleidiAI received identical context hashes and token counts and
returned byte-identical response hashes. Aggregate model compute fell from 26.7348 to 26.2351
seconds, a **1.8693% reduction**. Per-case changes were −2.3286% for `openapi-orders-v2` and
−1.4807% for `python-refund-v2`; every deterministic evidence gate still passed.

This is the prompt-plus-generation compute reported by `llama-server` inside complete frozen
quality requests. It excludes repository scanning, HTTP overhead, schema validation, evidence
gating, and report rendering, and each case was captured once per configuration. It is therefore
descriptive product-task evidence, not a repeated full end-to-end latency claim. The derivation is
reproducible with `scripts/analyze_model_quality.py`; see the
[machine-readable product-task summary](benchmarks/results/gha-30830782393-product-quality-summary.json).

## Measurement inventory

| Requested measure | Reported evidence | Scope or reason unavailable |
| --- | --- | --- |
| Time to first token | Not observed | ProofEdge deliberately uses non-streaming responses so a complete JSON object can be validated before publication. Non-streaming latency is not relabeled as TTFT. |
| Tokens per second | pp1024 +0.5604%; tg128 +4.2808% | 14 observations per configuration in the independent ABBA runtime comparison. |
| Product-task latency | Model compute 13.367 s mean → 13.118 s mean (−1.8693%) | Two frozen requests, byte-identical outputs; excludes non-model product stages. |
| Deterministic function latency | Warm p50 2.397 ms, p95 2.539 ms, cold 3.034 ms on latest main | Direct `evaluate_cases` static path; excludes interpreter/CLI startup, report I/O, and local-model inference. |
| p50 and p95 | Published for runtime throughput and deterministic CLI latency | The two product requests are reported individually; their descriptive p50/p95 are machine-readable but not treated as population estimates. |
| Peak RSS | Baseline 2,011,996 KiB; KleidiAI 2,012,040 KiB | `llama-bench` process peak; latest deterministic function benchmark peak is 24,516 KiB. |
| Model size | 1,066,227,264 bytes | Pinned Qwen2.5-Coder-1.5B-Instruct Q4_0 artifact. |
| Startup time | Not timestamped in the confirmation run | No startup claim is made. |
| CPU utilization | 387% mean for both builds | Four-thread `llama-bench` processes measured by `/usr/bin/time -v`. |
| Energy or power | Not measured | The hosted runner exposes no calibrated power telemetry. |
| Output quality | Both builds passed 2/2 cases; schema/reference/coverage 1.00 | Frozen golden objectives, raw responses, and byte-identical hashes retained. |
| Task success | Deterministic 2/2; model gate 2/2 per runtime | Small, disclosed challenge-created corpus. |
| Unsupported claims | Recall 1.00; false unsupported rate 0.00 | Deterministic golden evaluation, not broad real-world accuracy. |

## Honest evidence chain

The first ABBA profile was mixed: +0.5322% pp512 and −0.6967% tg128. It remains published in
[`benchmarks/results/gha-30822903168-summary.json`](benchmarks/results/gha-30822903168-summary.json).
Exploratory run
[`30828989800`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30828989800)
then selected a profile using predeclared rules. Only the later, separately launched run above is
used for the confirmed claim.

An independent usefulness audit later found that the revision-1 model gate validated citations
and objective anchors but did not reject a semantically wrong `equal` relation. Revision-2 canary
run [`30874565788`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30874565788)
therefore added purpose, input, and relation checks. It rejected all four model configurations
because the Python case cited valid lines but proposed unchanged behavior. Its attractive runtime
result (+0.9021% prompt processing, +6.1295% generation) is preserved but explicitly ineligible
for the product claim. See the
[canary summary](benchmarks/results/gha-30874565788-semantic-canary-summary.json) and
[complete raw evidence](benchmarks/raw/gha-30874565788).

Instrumented canary
[`30875555758`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30875555758)
then proved that repeated client TTFT, task latency, startup, and resource capture worked, but all
quality runs still failed because the compact model tried to infer equality or intent from code
alone. That run is also excluded and retained in its
[canary summary](benchmarks/results/gha-30875555758-semantic-canary-summary.json) and
[raw evidence](benchmarks/raw/gha-30875555758). The next frozen revision removes that unsafe
freedom: code-only proposals are `investigate`, and the optimized prompt receives a bounded,
prompt-injection-redacted source/target diff.

The bootstrap ranges in the summary resample observations within processes and are descriptive;
they are not confidence intervals across independent hosts. `llama-bench` is not end-to-end
product latency, and no energy claim is made. Full protocol, artifacts, and qualifications are in
[`benchmarks/README.md`](benchmarks/README.md).
