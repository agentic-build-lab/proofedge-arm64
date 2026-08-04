# Benchmarks

## Final Arm64 result

ProofEdge's release claim comes from native run
[`30880259094`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30880259094)
at project commit `6d828a9e4416af70f56bb8f7b370cc9568916ef2`. The model, quantization,
`llama.cpp` commit, VM class, workload, and thread count were identical; the causal build change
was `GGML_CPU_KLEIDIAI=OFF` versus `ON`.

| Metric | Baseline | KleidiAI | Change |
| --- | ---: | ---: | ---: |
| Prompt processing, pp1024 | 96.6036 tok/s | 97.1860 tok/s | **+0.6029%** |
| Token generation, tg128 | 34.7734 tok/s | 36.9914 tok/s | **+6.3783%** |

Four fresh `llama-bench` processes ran in ABBA order with seven observations per block: 14 per
build. The native runner reported `aarch64` and Neoverse N2. The selected profile remained 4
threads, KleidiAI chunk multiplier 1, batch 1024, and micro-batch 256. Runtime logs proved I8MM Q4
kernel selection. Peak RSS was 2,011,996 KiB baseline and 2,012,040 KiB KleidiAI; mean observed
CPU utilization was 387.0% and 386.5%, respectively.

The four baseline/optimized × KleidiAI-off/on quality ledgers all passed 2/2 frozen cases. Schema
completion, compiled-reference validity, semantic-objective coverage, and risk-evidence coverage
were 1.00, with zero canary leakage and zero fallback. Raw model reference validity remained
visible rather than being relabeled: 0.50 in the baseline build and 0.75 in the KleidiAI build.
The raw and compiled plans, compiler provenance, logs, environment, binaries, and a verified
81-file SHA-256 manifest are retained in the
[complete raw bundle](benchmarks/raw/gha-30880259094).

## Repeated product-task timing

Each build ran the complete frozen two-case ProofEdge model task five times in a persistent Python
process. Every run passed. Published compiled-plan hashes were stable within each build and
identical across builds. Raw model response hashes and completion token counts differed, so the
analyzer explicitly marks exact model-compute comparison ineligible.

| Client-observed measure | Baseline | KleidiAI | Descriptive change |
| --- | ---: | ---: | ---: |
| Full two-case task, p50 | 45.387 s | 44.639 s | **−1.648%** |
| Full two-case task, p95 | 45.464 s | 44.688 s | **−1.706%** |
| Request TTFT, p50 (n=10) | 14.960 s | 14.867 s | **−0.622%** |
| Request TTFT, p95 (n=10) | 20.025 s | 19.969 s | **−0.280%** |
| Request end-to-end, p50 (n=10) | 22.674 s | 22.314 s | **−1.587%** |
| Request end-to-end, p95 (n=10) | 27.701 s | 27.661 s | **−0.146%** |

TTFT compares the same prompts before response divergence. Full-task and request end-to-end
changes are descriptive product observations, not an isolated KleidiAI kernel effect. The
machine-readable derivation is in
[`gha-30880259094-product-quality-summary.json`](benchmarks/results/gha-30880259094-product-quality-summary.json).

## Measurement inventory

| Requested measure | Reported evidence | Scope or reason unavailable |
| --- | --- | --- |
| Time to first token | p50 14.960 → 14.867 s; p95 20.025 → 19.969 s | Client-observed first non-empty streamed content, 10 requests per build. |
| Tokens per second | pp1024 +0.6029%; tg128 +6.3783% | 14 observations per build in the same-host ABBA runtime comparison. |
| Product-task latency | p50 45.387 → 44.639 s; p95 45.464 → 44.688 s | Five complete two-case trials per build; descriptive because raw outputs differed. |
| Deterministic function latency | Warm p50 2.357 ms, p95 2.419 ms, cold 2.788 ms | 30/30 passes in main run `30882095544`; direct static path excludes local inference. |
| Peak RSS | Runtime: 2,011,996 vs 2,012,040 KiB; server: 2,094,936 vs 2,091,712 KiB | Process-level maxima; client and server are not falsely summed into a whole-system peak. |
| Model size | 1,066,227,264 bytes | Pinned Qwen2.5-Coder-1.5B-Instruct Q4_0 artifact. |
| Startup time | Baseline mean 2,026.7 ms; KleidiAI mean 2,020.0 ms | Three server startups per build on one hosted VM. |
| CPU utilization | Runtime mean 387.0% vs 386.5%; server capture 383% vs 383% | Four-vCPU process observations, not energy. |
| Energy or power | Not measured | The hosted runner exposes no calibrated power telemetry. |
| Output quality | Four configurations passed; compiled references, semantics, and coverage 1.00 | Raw validity 0.50/0.75 and compiler provenance are separately disclosed. |
| Task success | Product trials 5/5 per build; model gate 2/2 per configuration | Small, disclosed challenge-created corpus. |
| Unsupported claims | Recall 1.00; false unsupported rate 0.00 | Deterministic golden evaluation, not broad real-world accuracy. |

## Honest evidence chain

The first ABBA profile was mixed: +0.5322% pp512 and −0.6967% tg128. It remains published in
[`benchmarks/results/gha-30822903168-summary.json`](benchmarks/results/gha-30822903168-summary.json).
Exploratory run
[`30828989800`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30828989800)
then selected a profile using predeclared rules. Run
[`30830782393`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30830782393)
initially confirmed its runtime gain under the revision-1 gate; the audit below later showed why
that gate could not authorize a final product claim. Only final revision-3 run `30880259094` is
used for the release claim.

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

Third canary
[`30876839849`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30876839849)
confirmed that constraint but exposed two remaining evidence defects: the compact model cited
unnumbered diff positions for OpenAPI and copied generic few-shot terms into Python proposals.
The unchanged semantic gate rejected all configurations, so its positive runtime result
(+0.7099% prompt processing, +3.4337% generation) is ineligible. The complete
[canary summary](benchmarks/results/gha-30876839849-semantic-canary-summary.json) and
[raw evidence](benchmarks/raw/gha-30876839849) are retained. The next revision replaces the
ambiguous diff with a generic ranked change map whose source and target excerpts preserve real
repository line numbers, and removes contaminating few-shot examples.

Fourth canary
[`30878319904`](https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30878319904)
showed that the numbered change map fixed prompt contamination but did not make a 1.5B model a
reliable specification writer: it found `refund`, `1.005`, and `201`/`200`, yet still mixed source
and target coordinates, preferred API metadata in some runs, and wrote “ensure” instead of an
explicit comparison. The frozen gate again rejected all configurations; its +0.8626% prompt and
+4.7830% generation results are excluded. See the
[canary summary](benchmarks/results/gha-30878319904-semantic-canary-summary.json) and
[raw evidence](benchmarks/raw/gha-30878319904).

The next revision changes authority rather than the oracle: the model ranks migration risks, then
a deterministic AST/OpenAPI compiler instantiates the published scenario, source-versus-target
purpose, and citable line. The raw model plan and the compiled plan are both retained. A safety
floor can restore a high-risk mechanically detected candidate that the model missed, so compact
model wording can no longer silently decide what becomes evidence.

Final run `30880259094` passed the unchanged semantic objectives and the new compiled-reference
gate in all four configurations. For the optimized profile, the Python signature candidate was
model-aligned while the Python body change and OpenAPI status change were restored by the
deterministic safety floor. That provenance is part of the evidence, not hidden. All five repeated
product trials per build produced stable, cross-build-identical compiled plans; raw model outputs
remained distinct and therefore exclude an exact model-compute comparison.

The bootstrap ranges in the summary resample observations within processes and are descriptive;
they are not confidence intervals across independent hosts. `llama-bench` is not end-to-end
product latency, and no energy claim is made. Full protocol, artifacts, and qualifications are in
[`benchmarks/README.md`](benchmarks/README.md).
