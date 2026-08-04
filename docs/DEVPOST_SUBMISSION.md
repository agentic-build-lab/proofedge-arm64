# ProofEdge — Devpost Submission Copy

## Submission metadata

- **Track:** Cloud AI
- **Project status:** New project created during the challenge period
- **License:** MIT
- **Repository:** https://github.com/agentic-build-lab/proofedge-arm64
- **Arm developer tools:** KleidiAI through the pinned `llama.cpp` Arm CPU backend

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

The same frozen product requests returned byte-identical response hashes across both runtimes.
Their aggregate prompt-plus-generation model compute fell from 26.7348 to 26.2351 seconds, a
descriptive **1.8693% reduction**. Each case was captured once, so we do not present that number as
a repeated full end-to-end claim.

These are same-model runtime-throughput measurements, not end-to-end latency or energy claims.
Raw JSON, stderr, CMake caches, binary identities, environment metadata, quality ledgers, and
self-verifying hashes are public.

## Why ProofEdge should win

ProofEdge makes optimization evidence part of the product contract. A faster runtime cannot ship
unless the same frozen migration objectives, exact evidence references, injection canaries, and
fallback rules still pass. Judges can inspect the first negative result, the predeclared tuning
policy, the independent confirmation, runtime I8MM proof, byte-identical product responses, and
every raw hash. That combination turns an Arm kernel improvement into a trustworthy private-AI
workflow instead of a benchmark screenshot.

The project is useful beyond the challenge: migration review is privacy-sensitive, expensive to
outsource, and unusually vulnerable to plausible unsupported claims. CPU-only Arm64 inference
keeps source local, and ProofEdge's deterministic gate makes a compact model safe enough to assist
without becoming the authority.

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
- 38 automated tests, 84%+ Python coverage, pinned CI actions, hash-locked development
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
- Product-task timing: https://github.com/agentic-build-lab/proofedge-arm64/blob/main/benchmarks/results/gha-30830782393-product-quality-summary.json

## Arm / Arm64 setup instructions

### Fast credential-free verification

On any Python 3.11+ machine:

```bash
git clone https://github.com/agentic-build-lab/proofedge-arm64.git
cd proofedge-arm64
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
proofedge evaluate --cases evaluation/cases --output evaluation/results/deterministic.json
proofedge analyze \
  --source evaluation/cases/python-refund-v2/source \
  --target evaluation/cases/python-refund-v2/target \
  --manifest evaluation/cases/python-refund-v2/manifest.json \
  --output reports/python-refund-v2
```

The analyzer writes `report.md` and `evidence-ledger.json` and does not execute repository code or
require a model credential.

### Reproduce the native Arm64 result

Use a genuine `aarch64` machine with four or more CPU cores, CMake, Ninja, Python 3.12, and enough
space for the pinned 1,066,227,264-byte Q4_0 model. The exact model revision/SHA-256, `llama.cpp`
commit, compiler flags, workload, and profile are frozen in
`benchmarks/config/arm64-confirm-v1.json`.

From an authenticated GitHub CLI session, the one-command native workflow is:

```bash
gh workflow run arm64-llama-bench.yml --ref main
```

It runs only on GitHub's native `ubuntu-24.04-arm` runner, builds KleidiAI off/on, executes ABBA
blocks, runs the model-quality matrix, proves the selected I8MM Q4 kernel from runtime logs, and
uploads a hash-manifested raw evidence bundle. To inspect the confirmed run without rerunning it:

```bash
gh run download 30830782393 --dir downloaded-evidence
cd downloaded-evidence/*
sha256sum --check SHA256SUMS
```

No paid API, hosted model, secret, GPU, or emulation is required. Full manual steps and known
mutable inputs are documented in `docs/REPRODUCIBILITY.md`.

## Built with

Arm64, KleidiAI, `llama.cpp`, Qwen2.5-Coder, Python, JSON Schema, GitHub Actions, React, vinext,
Cloudflare Workers, HyperFrames, and Kokoro.
