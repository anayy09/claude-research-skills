# Contributing

Thanks for helping grow this collection. Whether you're fixing a typo or adding
a whole new skill, this guide keeps every contribution consistent with the rest.

## Ways to contribute

- **Improve an existing skill**: sharper instructions, better references, a bug
  fix in a script. Bump the skill's `version` (see [Versioning](#versioning)).
- **Add a new skill**: the main event; see below.
- **Report a bug or propose a skill**: open an [issue](https://github.com/anayy09/claude-research-skills/issues/new/choose).

## Anatomy of a skill

A skill is a single directory at the repository root. The only hard requirements
are `SKILL.md` and `README.md`; everything else is optional and loaded on demand.

```
my-skill/
├── SKILL.md          REQUIRED   the instructions the agent loads
├── README.md         REQUIRED   human-facing docs (use an existing skill as a template)
├── references/       optional   knowledge the agent reads when relevant
├── scripts/          optional   runnable helpers (document deps in the README)
├── assets/           optional   templates, data files
├── examples/         optional   worked end-to-end walkthroughs
└── templates/        optional   output scaffolds
```

Keep the folder name `kebab-case` and identical to the `name` in the frontmatter.

## SKILL.md frontmatter spec

Every `SKILL.md` starts with a YAML frontmatter block. These fields are the
standard for this repository:

```yaml
---
name: my-skill                 # REQUIRED: kebab-case, matches the folder name
description: >-                # REQUIRED: when the agent should invoke this skill.
  Use when ... Triggers on ... # Front-load concrete triggers; this is how Claude
  ... Prefer this over ...     # decides to load the skill, so be specific.
summary: "One crisp line for the catalog table."   # REQUIRED
version: "1.0.0"               # REQUIRED: semantic version (see below)
author: anayy09                # REQUIRED: your GitHub username
license: MIT                   # REQUIRED
metadata:
  status: active               # active | experimental | deprecated
  last_updated: "2026-07-25"   # ISO date of the last meaningful change
---
```

- **`description`** is the most important field. It is the only thing the agent sees
  when deciding whether to use the skill. Lead with the situations and literal
  trigger phrases that should activate it.
- **`summary`** is the human one-liner shown in the README catalog. Keep it under
  ~100 characters. Avoid a leading `Use when...`; describe the value.
- Additional fields (e.g. `allowed-tools`, `compatibility`, `related_skills`) are
  fine, so preserve any a skill already declares.

## Versioning

Each skill is versioned independently with [SemVer](https://semver.org):

| Bump  | When |
| :---- | :--- |
| MAJOR | Behavior or output contract changes (could surprise an existing user). |
| MINOR | New capability, backward compatible. |
| PATCH | Fixes, wording, references. No behavior change. |

Record the change in your skill README's **Changelog** section and, if it's
notable, in the repo-level [`CHANGELOG.md`](./CHANGELOG.md).

## Submitting a change

1. **Fork and branch** from `main` (e.g. `add-my-skill`).
2. **Build the skill** to the structure above. Copy an existing README as a
   template so the voice and sections match.
3. **Regenerate the catalog** so the README table includes your skill:
   ```bash
   pip install pyyaml          # one-time
   python scripts/generate_catalog.py
   ```
4. **Validate locally** (the same checks CI runs):
   ```bash
   python scripts/validate_skills.py
   python scripts/generate_catalog.py --check
   ```
5. **Check it packages** if you added or moved files. Release assets are built
   from the skill folder, and the archive must be rooted at that folder:
   ```bash
   python scripts/package_skills.py --skill my-skill
   ```
6. **Open a pull request** using the template. Explain what the skill does and why
   it belongs here.

Releases are cut by tagging `vX.Y.Z` on `main`. That triggers
`.github/workflows/release.yml`, which validates the collection, builds a zip per
skill plus a combined bundle, and attaches them to the GitHub Release with
checksums. The download links in the README catalog point at
`releases/latest/download/<skill>.zip`, so they pick up the new assets with no
edit.

## Style

- Write like a practitioner, not a brochure. Concrete beats grand.
- Prose in `SKILL.md` and references should be plain and skimmable.
- Scripts should degrade gracefully (no hard crash when a network call fails) and
  never silently pass a check they couldn't actually perform.

## Scope

This collection is opinionated toward **research and technical workflows**. A
skill for writing haikus is lovely but out of scope; a skill for wrangling BibTeX
is right at home. If unsure, open a proposal issue first.
