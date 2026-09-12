# RUNBOOK.md

Operational commands for `{{PROJECT}}`. Written by hand, unlike the logs, and
holds no results: only commands, where they leave off, and how to stop and
resume. Commands are given in the shell the owner uses (state which).

## State as of {{DATE}}

What is running, what is paused, what the brake is. Nothing running and no
brake on is a valid state and is said explicitly.

## Environment

Interpreter path, data root, environment variables, GPU and memory limits,
and the commands that must be handed to the owner rather than run by the
agent (data loads that saturate memory, training runs longer than the
session). See `references/long-runs.md` in the skill for the rules.

## Long-running work

Every long job:

- reads a `STOP` file in its working directory at each checkpoint and exits
  cleanly when it exists (`touch STOP` to pause, delete it and rerun to
  resume);
- writes a `progress.json` (step, total, elapsed, ETA, last checkpoint) that
  the agent polls instead of tailing logs;
- resumes from its last checkpoint when rerun with the same command;
- is launched by a command recorded here, with the exact resume command
  beside it.

```
# launch
<command>

# pause
<command that creates STOP>

# resume
<the same launch command>

# check
<command that prints progress.json>
```

## Do not run

Commands that were tried and must not be repeated, with the reason.
