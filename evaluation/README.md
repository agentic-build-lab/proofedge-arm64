# Golden Evaluation Corpus

This corpus was frozen before local-model and runtime optimization. It prevents latency work from
quietly eroding product usefulness.

The credential-free evaluator covers deterministic static checks only. Its case-pass rate and
category recall are not presented as local-model task accuracy. Claim metrics are defined over
the declared claims in each manifest: unsupported-claim recall measures known unsupported claims
that were rejected, while false-unsupported-claim rate measures supported claims rejected in
error. Local-model quality is evaluated in a separate inference harness.

## Included cases

1. `python-refund-v2`: a challenge-created, MIT-licensed Python API migration with a changed
   signature, an unsupported completeness claim, and a repository prompt injection. The code is
   deliberately tiny so every expected finding can be audited by eye.
2. `openapi-orders-v2`: a challenge-created, MIT-licensed service-contract migration that changes
   a response status and drops the target tests.
3. `qs-go-external.json`: metadata-only reference to the separately published `qs-go` port and its
   upstream behavioral oracle. ProofEdge does not copy that project and does not count it as new
   work. A pinned fetch-and-evaluate adapter will be added separately.

The first two cases are synthetic controls, not claims about defects in third-party software. The
third case is an external public corpus and is disclosed as pre-existing work.

Run the credential-free evaluation:

```bash
proofedge evaluate --cases evaluation/cases --output evaluation/results/latest.json
```
