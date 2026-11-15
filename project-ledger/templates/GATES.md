# GATES.md

Gate ledger for `{{PROJECT}}`. A gate is a claim about the project that a
command can check. A gate is met when its CHECK has been run from the
repository root, its output contained EXPECT, and the EVIDENCE line records
that run. A ticked box with no EVIDENCE line is not a met gate.

`python scripts/project_ledger.py gates --run` runs every CHECK;
`--record` writes the EVIDENCE line and ticks the box on success. Run it
before every hand-off and before every commit that claims a phase is done.

A CHECK runs through the system shell: `cmd.exe` on Windows, `/bin/sh`
elsewhere, never PowerShell. Write it to work in both (a `python` command
or a script), with double quotes around arguments. `{skills}` in a CHECK
stands for the folder that holds the installed skills; the script fills it
in when it runs the check.

Format (lines inside a code fence are examples; the script does not read
them as gates):

```
- [ ] P1G1: <the claim, stated so a stranger could check it>
  CHECK: <command, run from the repository root>
  EXPECT: <text the output must contain>
  EVIDENCE: <written by the script: shell, cwd, exit code, date, last line>
```

A gate id is `G` and a number, after an optional prefix of capitals and
digits that names the phase: `P0G1` for phase P0, `SG1` for submission.
A line whose id does not have that shape is not a gate to the script.

## P0

- [ ] P0G1: the pre-registration is committed and tagged prereg-v1, and every run manifest was committed after the tagged commit and created after it
  CHECK: python scripts/project_ledger.py prereg --tag prereg-v1 --manifests "runs/*/manifest.json"
  EXPECT: PREREG OK

- [ ] P0G2: the ledger verifies clean
  CHECK: python scripts/project_ledger.py verify --git
  EXPECT: 0 failure(s)

- [ ] P0G3: AUTHORS.yaml is filled and every author has a name and an email
  CHECK: python -c "import yaml,sys; a=yaml.safe_load(open('docs/AUTHORS.yaml'))['authors']; assert a and all(x.get('name') and x.get('email') for x in a); print('AUTHORS OK')"
  EXPECT: AUTHORS OK

## Submission

- [ ] SG1: the built manuscript has no placeholder and its front matter matches AUTHORS.yaml
  CHECK: python "{skills}/build-check/scripts/build_check.py" submission/main.tex --no-build --authors docs/AUTHORS.yaml --strict
  EXPECT: PASS
