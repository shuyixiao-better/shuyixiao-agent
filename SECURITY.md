# Security Policy

## Supported versions

Security fixes are applied to the latest commit on `main`. No separately supported release line exists yet.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting feature for this repository. If it is unavailable, contact the maintainer using the address in `pyproject.toml`. Do not include secrets, exploit payloads, or sensitive user data in a public issue. You should receive an acknowledgement when the maintainer has reviewed the report; a remediation timeline depends on severity and reproducibility.

## Secret management

- Never commit `.env`, API keys, tokens, or credential-bearing logs.
- Keep placeholders only in `.env.example`; rotate a credential immediately if it is exposed.
- CI and offline tests must run without real credentials.
- Prefer environment variables or a dedicated secret manager in deployments.

## API and transport safety

TLS certificate verification is enabled by default. Disabling `SSL_VERIFY` weakens transport security and should only be a temporary diagnostic measure on a trusted network. Restrict API keys to the minimum scope and monitor provider usage.

## Tool execution safety

Agent-selected tools can read files, make network requests, or consume resources. Treat model output as untrusted input: allowlist tools and paths, validate arguments, apply timeouts and resource limits, and require human confirmation for destructive or externally visible actions. Do not expose the demo Web service directly to an untrusted network without authentication and additional hardening.

## Prompt injection and RAG

Web pages, uploaded files, retrieved passages, and tool results may contain prompt injection. Keep instructions separate from retrieved content, label provenance, constrain tool authority, and do not let retrieved text override system policy. Validate upload paths and file types, limit size, isolate tenant collections, and consider poisoning or sensitive-data leakage when ingesting documents.

## Dependencies

Review Dependabot alerts and lockfile changes before merging. Rebuild environments from lockfiles where applicable and avoid installing packages from untrusted indexes.

This policy does not assert that the repository has no vulnerabilities.
