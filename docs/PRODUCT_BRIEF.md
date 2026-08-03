# Product Brief

## One-sentence promise

ProofEdge finds migration claims that are not supported by evidence, then generates the smallest
useful differential-testing plan to close the gap — locally on Arm64.

## Judge-facing demonstration

The demo will run one pinned migration case twice on the same native Arm64 host:

- baseline runtime and whole-repository prompt;
- KleidiAI-enabled runtime and evidence-selected prompt.

It will show time to first token, throughput, peak RSS, end-to-end latency, task success, and
unsupported-claim rate. The product must catch a seeded semantic defect and link the finding to
file-and-line evidence while treating a prompt injection inside the repository as untrusted text.

## Users

- maintainers accepting language or framework migrations;
- platform teams validating AI-generated rewrites;
- consultants who need an auditable handoff artifact;
- developers working with private repositories on CPU-only infrastructure.

## Non-goals

- proving full semantic equivalence;
- executing arbitrary repository scripts without an explicit allowlist;
- claiming energy improvements without calibrated power measurements;
- hiding model, hardware, failed-run, or quality-regression details.

## Provisional winning claim

On a fixed, public migration-assurance corpus, ProofEdge's Arm64-optimized inference and
evidence-selection pipeline will reduce end-to-end latency and memory pressure without exceeding
the predeclared quality-regression budget. This sentence becomes a measured claim only after the
raw native-Arm benchmark set is complete.

