# ProofEdge public demo

This directory contains the deployable, credential-free ProofEdge experience.
It presents the verified project narrative, exposes the raw native Arm64
evidence, and includes an interactive replay of the deterministic evidence
gate. The replay is intentionally labeled: it does not run a language model in
the browser and does not execute repository code.

## Local development

Requires Node.js 22.13 or newer.

```bash
npm ci
npm run dev
```

Open `http://localhost:3000`.

## Validation

```bash
npm run lint
npm test
npm audit --omit=dev
```

`npm test` creates the production vinext bundle and checks the server-rendered
HTML for the benchmark qualifications, public evidence link, replay entrypoint,
and absence of starter-preview residue.

## Scope

- Public, static project story and evidence links
- Client-side replay over a frozen public fixture
- No credentials, analytics, database, or remote model calls
- Social preview generated specifically for ProofEdge

The implementation and all benchmark artifacts live in the repository root.
See the main [ProofEdge README](../README.md) for the command-line product and
native Arm64 reproduction workflow.
