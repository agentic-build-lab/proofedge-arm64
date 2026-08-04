# ProofEdge — Devpost Submission Copy

## Tagline

Evidence before confidence: private migration assurance with a quality-gated local model and a
confirmed KleidiAI speedup on native Arm64.

## Inspiration

AI can rewrite a service in minutes, but speed creates a new review problem: how do we prove that
rounding, error behavior, status codes, and test coverage survived the migration? A plausible
answer is not enough for a private codebase. We wanted a tool that makes every useful AI
suggestion traceable—and makes every performance claim falsifiable.

## What it does

ProofEdge compares source and target repositories without executing them. It maps public
contracts, identifies semantic and coverage risks, checks declared migration claims, and asks a
compact local model for a small differential-testing plan. Model proposals enter the final
evidence ledger only when their schema, file, line, and model-visible context references pass a
deterministic gate.

The public demo replays a frozen refund migration where an optional argument disappears while the
migration still claims compatibility. ProofEdge cites the source and target evidence, proposes the
boundary test, and refuses the unsupported claim. Private code can remain on the Arm64 machine;
the demo uploads nothing and uses no hosted model API.

## How we built it

The core is a Python 3.11 package with a bounded, non-executing scanner, deterministic contract and
claim analysis, evidence-selected context, a strict local-model client, objective-based model
evaluation, and Markdown/JSON reporting. Repository instruction-like text is replaced with typed
hash placeholders before model inference. The loopback client disables proxies, redirects, prompt
caching, non-loopback DNS targets, and oversized responses.

The inference path pins `llama.cpp`, Qwen2.5-Coder-1.5B-Instruct Q4_0, and model bytes by SHA-256.
For Arm optimization we compiled the exact same runtime with KleidiAI disabled and enabled. A
predeclared exploratory sweep selected four threads, chunk multiplier 1, batch 1024, and
micro-batch 256. We committed that profile before launching the independent confirmation.

## Arm optimization and measured result

On a genuine `aarch64` Neoverse N2 GitHub runner, four fresh processes ran in ABBA order. Source,
model, quantization, VM, workload, and threads stayed fixed; only `GGML_CPU_KLEIDIAI` changed.
Runtime logs proved selection of the I8MM Q4 kernel.

- pp1024: 96.7379 → 97.2800 tokens/s, **+0.5604%**
- tg128: 35.2443 → 36.7531 tokens/s, **+4.2808%**

Both baseline and KleidiAI separately passed 2/2 frozen optimized-context model cases with schema
completion 1.00, raw-reference validity 1.00, risk-evidence coverage 1.00, zero canary leakage,
and zero fallback. We retained the first mixed profile (+0.532% prompt processing, −0.697%
generation) instead of hiding it, then separated tuning from confirmation.

These are same-model runtime-throughput measurements, not end-to-end latency or energy claims.
Raw JSON, stderr, CMake caches, binary identities, environment metadata, quality ledgers, and
self-verifying hashes are public.

## Challenges we ran into

The hardest part was resisting convenient but invalid comparisons. Identical model bytes do not
prove identical useful output, repeated samples inside one process are not independent hosts, and
build-time KleidiAI enablement does not prove that an Arm kernel ran. We therefore built separate
quality objectives, process-level ABBA blocks, runtime-log gates, and an explicit selection versus
confirmation boundary.

Untrusted repositories created a second challenge. We hardened directory traversal, local HTTP,
schema validation, report rendering, prompt-injection handling, and fallback attribution, then
added adversarial tests rather than relying on the prompt alone.

## Accomplishments that we are proud of

- A useful local-first product, not a benchmark wrapper.
- A positive independent Arm64 confirmation after publishing an earlier negative result.
- Quality gates that can veto an apparently faster runtime.
- 35 automated tests, 85%+ Python coverage, pinned CI actions, hash-locked development
  dependencies, and zero production npm audit findings.
- A public demo, complete evidence bundle, threat model, and reproducible build path.

## What we learned

Optimization evidence is strongest when every layer has a name and a boundary: kernel, serving
profile, model quality, and product workflow. Arm-specific kernels matter, but the release gate is
what makes the result trustworthy. Small local models become much more useful when their authority
is constrained by deterministic evidence.

## What's next

We plan to add larger pre-frozen migration corpora, a streaming product path for honest TTFT,
process-level repetition across several native hosts, safe user-approved test execution, and
energy measurements only on calibrated hardware.

## Try it out

- Demo: https://github.com/agentic-build-lab/proofedge-arm64
- Video: https://youtu.be/iuY49KZkrSs
- Source: https://github.com/agentic-build-lab/proofedge-arm64
- Release: https://github.com/agentic-build-lab/proofedge-arm64/releases/tag/v1.0.0
- Confirmed evidence: https://github.com/agentic-build-lab/proofedge-arm64/blob/main/benchmarks/results/gha-30830782393-summary.json

## Built with

Arm64, KleidiAI, `llama.cpp`, Qwen2.5-Coder, Python, JSON Schema, GitHub Actions, React, vinext,
Cloudflare Workers, HyperFrames, and Kokoro.
