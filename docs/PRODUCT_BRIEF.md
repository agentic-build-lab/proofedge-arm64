# Product Brief

## One-sentence promise

ProofEdge finds migration claims that are not supported by evidence, then proposes the smallest
useful differential-test plan to close the gap — locally on Arm64.

## Judge-facing demonstration

The public experience begins with a credential-free replay of a seeded migration defect. It shows
the bounded scan, deterministic findings, evidence references, an ignored prompt injection, and
the differential-test plan. The repository then exposes the native Arm64 evidence needed to audit
the local-inference path.

The benchmark story is intentionally causal:

1. same `llama.cpp` commit, model bytes, quantization, workload, threads, and native Arm64 VM;
2. KleidiAI disabled versus enabled in ABBA order;
3. serving settings tuned in a separately frozen exploration;
4. local-model usefulness judged by fixed evidence objectives and injection canaries.

## Users

- Maintainers accepting language or framework migrations
- Platform teams validating AI-generated rewrites
- Consultants who need an auditable handoff artifact
- Developers reviewing private repositories on CPU-only infrastructure

## Product boundary

The deterministic analyzer owns claims and evidence. The language model may propose tests, but it
cannot directly publish a proposal, add an unsupported migration claim, execute repository code,
or select arbitrary network targets. If the model fails, the product says so and falls back.

## Non-goals

- Proving full semantic equivalence
- Executing arbitrary repository scripts
- Claiming energy improvements without calibrated power measurements
- Hiding failed runs, hardware, model identity, or quality regression
- Describing a fixture replay as live inference

## Current measured claim

ProofEdge's final native Neoverse N2 ABBA run improves same-workload KleidiAI throughput by
**0.603% for pp1024** and **6.378% for tg128** versus the baseline build. All four quality
configurations pass 2/2 frozen cases with compiled references, semantic objectives, and risk
coverage at 1.00, with zero canary leakage and zero fallback. Five repeated product tasks per
build also pass with identical compiled published plans; their p50 changes from 45.387 to 44.639
seconds, reported descriptively because raw model outputs differ. The mixed first profile and four
failed semantic canaries remain public. No energy improvement is claimed.
