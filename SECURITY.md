# Security Policy

## Supported version

Security fixes are applied to the current `main` branch and the latest tagged release.

## Reporting a vulnerability

Please use this repository's **Security → Report a vulnerability** flow so details remain private.
Do not include secrets, private source code, or weaponized repository fixtures in a public issue.
Include the affected commit, operating system, minimal reproduction, impact, and any suggested
mitigation. This is a challenge project without a guaranteed response SLA.

## Safe deployment assumptions

ProofEdge is a local review tool, not a multi-tenant sandbox. Run it as an unprivileged user on a
stable copy of the repositories. Do not expose `llama-server` beyond loopback. Do not use an
untrusted model binary or GGUF outside an isolated environment. Review the
[threat model](docs/THREAT_MODEL.md) before processing adversarial input.

The analyzer does not execute repository code. This guarantee does not extend to commands a user
runs manually after reading its proposed differential tests.
