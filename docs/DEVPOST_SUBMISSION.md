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
compact local model to rank migration risks. A deterministic AST/OpenAPI compiler then creates a
small executable differential-testing plan with explicit source-versus-target purpose and visible
file-and-line evidence. Raw model wording is retained for audit but cannot directly become a
published claim.

The public demo replays a frozen refund migration where an optional argument disappears while the
migration still claims compatibility. ProofEdge cites the source and target evidence, proposes the
boundary test, and refuses the unsupported claim. Private code can remain on the Arm64 machine;
the demo uploads nothing and uses no hosted model API.

## How we built it

The core is a Python 3.11 package with a bounded, non-executing scanner, deterministic contract and
claim analysis, evidence-selected context, a strict local-model client, objective-based model
evaluation, a deterministic proposal compiler, and Markdown/JSON reporting. Compiler provenance
states whether each selected risk was model-aligned or restored by a safety floor. Repository
instruction-like text is replaced with typed hash placeholders before model inference. The
loopback client disables proxies, redirects, prompt caching, non-loopback DNS targets, and
oversized responses.

The inference path pins `llama.cpp`, Qwen2.5-Coder-1.5B-Instruct Q4_0, and model bytes by SHA-256.
For Arm optimization we compiled the exact same runtime with KleidiAI disabled and enabled. A
predeclared exploratory sweep selected four threads, chunk multiplier 1, batch 1024, and
micro-batch 256. We committed that profile before launching the independent confirmation.

## Arm optimization and measured result

On a genuine `aarch64` Neoverse N2 GitHub runner, four fresh processes ran in ABBA order. Source,
model, quantization, VM, workload, and threads stayed fixed; only `GGML_CPU_KLEIDIAI` changed.
Runtime logs proved selection of the I8MM Q4 kernel.

- pp1024: 96.6036 → 97.1860 tokens/s, **+0.6029%**
- tg128: 34.7734 → 36.9914 tokens/s, **+6.3783%**

All four baseline/optimized × KleidiAI-off/on quality configurations passed 2/2 frozen cases with
schema completion, compiled-reference validity, semantic-objective coverage, and risk-evidence
coverage at 1.00, zero canary leakage, and zero fallback. Raw-model reference validity is disclosed
separately at 0.50 baseline and 0.75 KleidiAI. We retained the first mixed profile and four failed
semantic canaries instead of hiding them.

The complete two-case product task was repeated five times per build and every run passed.
Published compiled-plan hashes were identical across builds. Task p50 changed from 45.387 to
44.639 seconds (**−1.648%**), streamed TTFT p50 from 14.960 to 14.867 seconds (**−0.622%**), and
request p50 from 22.674 to 22.314 seconds (**−1.587%**). Raw model outputs and completion token
counts differed, so these product timings are descriptive and we explicitly exclude an exact
model-compute or isolated-kernel attribution.

The ABBA figures are same-model runtime-throughput measurements. No energy claim is made. Raw
JSON, stderr, CMake caches, binary identities, environment metadata, quality ledgers, and 81
independently verified SHA-256 entries are public.

## Why ProofEdge should win

ProofEdge makes optimization evidence part of the product contract. A faster runtime cannot ship
unless the same frozen migration objectives, exact evidence references, injection canaries, and
fallback rules still pass. Judges can inspect the first negative result, four failed semantic
canaries, the predeclared tuning policy, runtime I8MM proof, stable compiled product plans, raw
model divergence, and every raw hash. That combination turns an Arm kernel improvement into a
trustworthy private-AI workflow instead of a benchmark screenshot.

The project is useful beyond the challenge: migration review is privacy-sensitive, expensive to
outsource, and unusually vulnerable to plausible unsupported claims. CPU-only Arm64 inference
keeps source local, and ProofEdge's deterministic gate makes a compact model safe enough to assist
without becoming the authority.

## Challenges we ran into

The hardest part was resisting convenient but invalid comparisons. Identical model bytes do not
prove identical useful output, repeated samples inside one process are not independent hosts, and
build-time KleidiAI enablement does not prove that an Arm kernel ran. An independent audit also
showed that valid citations can support semantically useless tests. We therefore built separate
quality objectives, process-level ABBA blocks, runtime-log gates, a deterministic proposal
compiler, and an explicit selection-versus-confirmation boundary.

Untrusted repositories created a second challenge. We hardened directory traversal, local HTTP,
schema validation, report rendering, prompt-injection handling, and fallback attribution, then
added adversarial tests rather than relying on the prompt alone.

## Accomplishments that we are proud of

- A useful local-first product, not a benchmark wrapper.
- A positive final Arm64 run after publishing an earlier negative result and four failed canaries.
- Quality gates that vetoed apparently faster runtimes four times before release.
- 57 automated tests, 85%+ Python coverage, pinned CI actions, hash-locked development
  dependencies, and zero production npm audit findings.
- A public demo, complete evidence bundle, threat model, and reproducible build path.

## What we learned

Optimization evidence is strongest when every layer has a name and a boundary: kernel, serving
profile, model quality, and product workflow. Arm-specific kernels matter, but the release gate is
what makes the result trustworthy. Small local models become much more useful when their authority
is constrained by deterministic evidence.

## What's next

We plan to add larger pre-frozen migration corpora, process-level repetition across several native
hosts, safe user-approved test execution, and energy measurements only on calibrated hardware.

## Try it out

- Demo: follow the local instructions in the repository
- Video: https://youtu.be/iuY49KZkrSs
- Source: https://github.com/agentic-build-lab/proofedge-arm64
- Release: https://github.com/agentic-build-lab/proofedge-arm64/releases/tag/v1.0.1
- Final runtime summary: https://github.com/agentic-build-lab/proofedge-arm64/blob/main/benchmarks/results/gha-30880259094-runtime-summary.json
- Product-task timing: https://github.com/agentic-build-lab/proofedge-arm64/blob/main/benchmarks/results/gha-30880259094-product-quality-summary.json
- Native action: https://github.com/agentic-build-lab/proofedge-arm64/actions/runs/30880259094

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
gh run download 30880259094 --dir downloaded-evidence
cd downloaded-evidence/*
sha256sum --check SHA256SUMS
```

No paid API, hosted model, secret, GPU, or emulation is required. Full manual steps and known
mutable inputs are documented in `docs/REPRODUCIBILITY.md`.

## Built with

Arm64, KleidiAI, `llama.cpp`, Qwen2.5-Coder, Python, JSON Schema, GitHub Actions, React, vinext,
Cloudflare Workers, HyperFrames, and Kokoro.
