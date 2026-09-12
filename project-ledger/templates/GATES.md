# GATES.md

Gate ledger for `{{PROJECT}}`. A gate is a claim about the project that a
command can check. A gate is met when its CHECK has been run from the
repository root, its output contained EXPECT, and the EVIDENCE line records
that run. A ticked box with no EVIDENCE line is not a met gate.

`python <skill>/scripts/project_ledger.py gates --run` runs every CHECK;
`--record` writes the EVIDENCE line and ticks the box on success. Run it
before every hand-off and before every commit that claims a phase is done.

Format:

```
- [ ] G1: <the claim, stated so a stranger could check it>
  CHECK: <command, run from the repository root>
  EXPECT: <text the output must contain>
  EVIDENCE: <written by the script: shell, cwd, exit code, date, last line>
```

## P0

- [ ] P0G1: the repository has git provenance and the pre-registration predates every run
  CHECK: git log --oneline -1 -- docs/PREREGISTRATION.md
  EXPECT: PREREGISTRATION

- [ ] P0G2: the ledger verifies clean
  CHECK: python scripts/project_ledger.py verify --git
  EXPECT: 0 failure(s)

- [ ] P0G3: AUTHORS.yaml is filled and every author has a name and an email
  CHECK: python -c "import yaml,sys; a=yaml.safe_load(open('docs/AUTHORS.yaml'))['authors']; assert a and all(x.get('name') and x.get('email') for x in a); print('AUTHORS OK')"
  EXPECT: AUTHORS OK

## Submission

- [ ] SG1: the built manuscript has no placeholder and its front matter matches AUTHORS.yaml
  CHECK: python <skill>/build-check/scripts/build_check.py submission/main.tex --no-build --authors docs/AUTHORS.yaml --strict
  EXPECT: PASS
