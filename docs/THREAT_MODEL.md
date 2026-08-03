# Threat Model

## Scope and assets

ProofEdge ingests two local repository trees, an optional JSON manifest, and optionally a response
from a loopback `llama-server`. Assets include private source text, file metadata, the integrity of
the report, host availability, and the user's trust in published evidence.

The filesystem, repository contents, manifest, model response, and local HTTP response are
untrusted. ProofEdge itself, its pinned dependencies, the selected GGUF, and the `llama.cpp`
binary are trusted only to the degree established by their hashes and execution environment.

## Threats and controls

| Threat | Control | Residual risk |
| --- | --- | --- |
| Repository code execution | The analyzer performs static reads only; it has no repository subprocess path | A user may manually execute a proposed test later |
| Symlink or junction escape | Link-like entries are skipped; file descriptors use `O_NOFOLLOW` where available; only regular bounded files are read | Concurrent filesystem mutation can still create races; analyze a stable snapshot |
| Resource exhaustion | Limits: 2,000 readable files, 512 KiB per file, 25 MiB total, 20,000 entries, depth 40, path length 1,000 | Worst-case parsing still consumes CPU inside those limits |
| Binary or malformed text | NUL-containing files are skipped; UTF-8 decode is replacement-safe; supported extensions are allowlisted | Polyglot text may still be misleading evidence |
| Prompt injection in source | Instruction-like lines are detected; every model-visible injection line becomes a typed SHA-256 placeholder | Novel phrasing may evade the detector, so model output is never trusted directly |
| Model hallucinated evidence | Closed response schema plus existence, line-range, and exact context-visibility checks | A valid line can be irrelevant; frozen objective scoring measures this separately |
| Schema smuggling | Unknown fields, wrong types, booleans-as-integers, invalid enums, missing or empty tests, oversized output, and malformed JSON are rejected | Correctly shaped but low-value content may remain |
| SSRF or credential leakage | Endpoint scheme and authority are parsed; credentials, path, query, and fragment are refused; DNS must resolve entirely to loopback | A compromised local process can impersonate the server |
| Proxy or redirect escape | Proxy handlers and redirects are disabled; requests carry no credentials; body cap is 1 MiB | Host networking itself remains outside the process boundary |
| Prompt-cache contamination | The client sends `cache_prompt: false`; benchmark servers use `--no-cache-prompt` | Other server-global state is controlled by running one slot and restarting per arm |
| Markdown injection | Untrusted strings are HTML-escaped and Markdown metacharacters are escaped or code-wrapped | Consumers that reinterpret the JSON ledger need their own output encoding |
| Evidence-path disclosure | Public reports store logical roots `source` and `target`, not absolute input paths | Source text and hashes are still sensitive and should not be published without review |
| Silent AI fallback | No accepted proposal sets engine to `deterministic-fallback`; CLI exits 2 | Callers must preserve and check exit status |
| Dependency substitution | Actions use full commit SHAs; Python dev packages and model/runtime commits are pinned; model and artifacts are hashed | Operating-system packages and hosted runner images are not content-addressed |

## Explicit non-guarantees

ProofEdge does not prove semantic equivalence, safely execute arbitrary tests, sanitize a hostile
GGUF, isolate tenants, or protect a host already compromised by another local process. It is an
evidence-gated review assistant, not a security boundary for executing untrusted code.

## Operational guidance

1. Work from read-only or disposable repository snapshots.
2. Run as an unprivileged user and keep the model server bound to `127.0.0.1`.
3. Verify the pinned GGUF SHA-256 before serving it.
4. Treat proposed tests as code-review suggestions until a human approves execution.
5. Keep the JSON ledger and `SHA256SUMS` beside the report for later verification.
