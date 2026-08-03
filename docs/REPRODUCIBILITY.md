# Reproducibility

## Source and dependency identity

- Every claim should name a ProofEdge commit.
- GitHub Actions are referenced by full commit SHA and checkout does not persist credentials.
- `requirements-dev.lock` pins Python build/test dependencies with distribution hashes.
- `demo/package-lock.json` pins the public demo dependency graph.
- Model repository, revision, filename, SHA-256, runtime commit, hardware class, and workload are
  stored in `benchmarks/config/llama-cpp-qwen15b-q4_0.json`.

## Local deterministic reproduction

Use Python 3.12 for the byte-for-byte CI environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-build-isolation --no-deps -e .
ruff check .
ruff format --check .
pytest --cov=proofedge --cov-report=term-missing --cov-fail-under=75
proofedge evaluate --cases evaluation/cases --output evaluation/results/deterministic.json
```

The result ledger includes sorted keys and logical repository roots. Timing naturally varies; the
deterministic findings and metrics should not.

## Native Arm workflows

From an authenticated GitHub CLI session:

```bash
gh workflow run arm64-llama-bench.yml --ref main
gh workflow run arm64-llama-tune.yml --ref main
```

Record the returned run IDs, wait for terminal conclusions, then download without renaming files:

```bash
gh run download RUN_ID --dir downloaded-evidence
```

Inside each artifact, verify:

```bash
cd downloaded-evidence/ARTIFACT_DIRECTORY
sha256sum --check SHA256SUMS
```

Review `project-commit.txt`, `llama-cpp-commit.txt`, the config copies, model SHA, binary hashes,
`architecture.txt`, `lscpu.json`, CMake caches, raw JSON, stderr, time logs, and quality ledgers.
The architecture must be genuine `aarch64`; emulated runs are invalid as performance evidence.

## Comparing results

Do not compare runs with different model bytes, quantization, source commit, context, sampling,
thread count, batch sizes, or hardware as if one variable caused the difference. Tuning runs are
for selection; confirmation runs are for claims. Report all selected metrics and any regression,
not only the favorable phase.

## Known non-content-addressed inputs

GitHub's hosted runner image and Ubuntu package mirrors are mutable. Each run captures OS, kernel,
CPU, compiler, and CMake facts to make drift visible. A fully hermetic toolchain is future work.
