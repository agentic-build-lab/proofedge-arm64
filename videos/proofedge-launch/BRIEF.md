---
workflow: product-launch-video
flow: automation
storyboard: no
message: "ProofEdge turns AI-generated migrations into auditable evidence, with private local reasoning and measured optimization on real Arm64."
destination: youtube
aspect: 1920x1080
language: en
audience: "Arm challenge judges, ML systems engineers, and developer-infrastructure teams"
length: 168.767s
angle: "proof-first technical product launch"
narration: yes
voice: am_michael
style_preset: blue-professional
---

## Intent

Create a polished two-to-three-minute product-launch film for the Arm Create: AI Optimization Challenge. Open on the trust gap in AI-generated migrations, then show ProofEdge finding a concrete unsupported claim, constructing a differential test plan, and issuing an evidence ledger. Make the architecture and real Arm64 optimization legible without turning the film into a terminal screencast. The emotional arc is doubt to proof to deployable confidence.

## Assets

- ../../demo — local interactive product demo; capture its real interface and copy.
- https://github.com/agentic-build-lab/proofedge-arm64 — public source, reproducibility commands, and technical documentation.
- ../../benchmarks/results/gha-30822903168-summary.json — first independent native Arm64 A/B evidence.
- ../../benchmarks/results/gha-30828663605-summary.json — second native Arm64 A/B and quality-matrix evidence.
- ../../benchmarks/results/gha-30828989800-tuning-summary.json — frozen tuning decision evidence.
- ../../benchmarks/config/arm64-confirm-v1.json — precommitted confirmation profile.
- ../../benchmarks/results/gha-30830782393-summary.json — successful independent confirmation and quality gates.

## Customizations

- Use the actual public demo as the visual source of truth for product-interface shots.
- Show exact, labeled benchmark values and the Neoverse N2 / AArch64 environment; never imply that a sub-one-percent throughput change is a dramatic speedup.
- Make the larger optimization story explicit: evidence-gated structured output, compressed context, bounded execution, and an Arm-specific KleidiAI I8MM kernel selected on the frozen configuration.
- Include English narration and burned-in English captions for silent judging environments.
- End with reproducible commands, the public repository, and a clear Cloud AI positioning statement.

## Notes

- No paid media, cloud purchases, or metered generation.
- Do not cherry-pick or hide the first mixed result: the initial profile regressed decode, while the separately frozen profile later confirmed +0.56% pp1024 and +4.28% tg128.
- Distinguish deterministic static analysis latency from local-model inference performance.
- Keep all public wording professional, technically precise, and sourceable to repository artifacts.
