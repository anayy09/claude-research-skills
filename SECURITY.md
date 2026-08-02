# Security Policy

## Scope

These skills are instructions and helper scripts that run locally inside your own
Claude Code environment. They do not phone home. A few scripts make optional,
read-only network calls to public metadata APIs (for example Crossref to verify a
DOI); these degrade gracefully offline and never transmit your content.

## Reporting a vulnerability

If you find a security issue, for example a script that could be coerced into
writing outside its working directory, or a reference that leaks a secret, please
**do not open a public issue**.

Instead, report it privately through GitHub's
[private vulnerability reporting](https://github.com/anayy09/claude-research-skills/security/advisories/new).
Include a description, reproduction steps, and the affected skill and version.

You can expect an initial response within a few days. Confirmed issues will be
fixed promptly and credited (unless you prefer to remain anonymous).

## Handling secrets

Never commit API keys, tokens, or credentials to a skill. The repository's
`.gitignore` excludes common secret files, but the ultimate safeguard is you:
review your diff before pushing.
