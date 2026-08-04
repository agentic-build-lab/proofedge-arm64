# Threat Model

ProofEdge treats repository trees, manifests, model output, and loopback HTTP responses as
untrusted. Its protected assets are private source text, report integrity, host availability, and
the user's trust in published evidence.

Core controls include:

- bounded, non-executing repository ingestion with ignored-tree pruning, entry/depth/size caps,
  regular-file checks, and link rejection;
- typed SHA-256 placeholders for instruction-like repository content before it reaches the model;
- a closed local response schema plus exact path, line-range, and context-visibility gates;
- loopback-only model endpoints with credentials, proxies, redirects, non-loopback DNS results,
  and oversized responses rejected;
- explicit `deterministic-fallback` attribution and a nonzero exit when no model proposal survives;
- escaped report rendering and logical repository labels instead of absolute paths;
- pinned Actions, Python dependencies, model revision, runtime commit, and content hashes.

Residual risks remain. A valid source line can be semantically irrelevant; the frozen objective
gate measures but cannot eliminate that risk. Concurrent filesystem mutation may race a scan, a
compromised local process can impersonate the model server, and a proposed test becomes executable
code if a user chooses to run it later. ProofEdge is an evidence-gated review assistant, not a
sandbox or a proof of semantic equivalence.

Use read-only snapshots, run unprivileged, keep the model server on `127.0.0.1`, verify the GGUF
hash, and review proposed tests before execution. The complete threat/control/residual-risk matrix
is in [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md); disclosure guidance is in
[`SECURITY.md`](SECURITY.md).
