# Long-running work

Anything that outlives a turn: training, a sweep, a batch of API calls, a
download. The failure modes are specific: the agent sleeps in a loop and the
user asks "are you stuck?"; the job saturates the machine and freezes it; the
session ends and nobody knows how to resume; the job finishes and the result
is never logged.

## Before launching

1. **Estimate and say the cost.** Wall-clock at the measured rate (time one
   unit first), memory at peak, disk. If the estimate is longer than the
   session or heavier than the machine, do not launch: hand the command to
   the owner (below).
2. **Write the launch, pause, resume, and check commands into
   `RUNBOOK.md`** before running the launch. In the owner's shell. On
   Windows that is PowerShell, with paths quoted and no Bash-isms.
3. **Register the run** with `experiment-ledger` so the output directory has
   a manifest before the first result lands.
4. **Give the estimate before being asked, with its basis.** "About 7 hours
   per seed, from 650 s per epoch over 40 epochs on this GPU." Take the
   basis from the durations recorded in `RUNBOOK.md` when a comparable run
   exists, and from a timed unit otherwise. The same applies to any step
   of your own that will take more than a few minutes: say how long and
   why before starting it.
5. **Test the command you hand over.** Run it far enough to see it start
   (a dry run, one step, or `--help` with the real arguments) in the shell
   it is written for. A command with a broken quote or a stale data path
   costs the owner a session.

## Every long job implements

- **A STOP file.** At each checkpoint the job checks for `STOP` in its
  working directory and exits cleanly when it exists. Pausing is `touch
  STOP` (PowerShell: `New-Item STOP -ItemType File`); resuming is deleting
  it and rerunning the same command.
- **A progress file.** `progress.json` with step, total, elapsed seconds,
  estimated remaining, and the last checkpoint path, rewritten at every
  checkpoint. The agent reads this file; it does not tail a log.
- **Resume from checkpoint** when rerun with the same command. A job that
  restarts from zero on rerun is not resumable and is said so in the runbook.
- **Exit codes and a last line.** Non-zero on failure; a final line that
  states what was produced.

## While it runs

- Poll the progress file at an interval matched to the job (minutes, not
  seconds), or wait on a monitor that fires when the output lands. Never
  `sleep` in a loop; never re-read a log every few seconds.
- Do other work that does not depend on the result, and say what is running
  when asked, from the progress file: step, rate, ETA.
- When the user says stop: create the STOP file, wait for the clean exit,
  record where it stopped in `RUNBOOK.md`, and append a `PROGRESS.md` entry
  with the resume command. "Peacefully" means the checkpoint is intact and
  the resume is one command.
- When it finishes, record the actual wall-clock, rate, and machine beside
  the launch command in `RUNBOOK.md`. The next estimate is read from there.
- When the user reports that they started a run themselves, set a monitor
  on its progress file or output and pick the work up when it lands,
  without being asked a second time.

## Handing a command to the owner

Do this, rather than running it, when:

- the machine cannot take it (a data load that saturates RAM, a training
  run on a laptop GPU that will take hours and freeze the desktop);
- it needs a credential the agent should not hold (a cookie, a token typed
  interactively);
- the owner asked to run heavy jobs themselves.

Give one command block in the owner's shell with the working directory,
environment variables, and the exact invocation; say what to report back
(the last line, the path of `progress.json`); then wait. When the result
arrives, log it before doing anything else.

## When it finishes

1. Append the `RESULTS-LOG.md` entries with intervals, citing the run id.
2. Append the `PROGRESS.md` `RUN` entry with counts.
3. Update `RUNBOOK.md` state to "nothing running".
4. Run the gates that read the new artifact.

## Machine limits worth writing down

Put these in `RUNBOOK.md` Environment so a new session inherits them: total
RAM and the largest array that fits, GPU memory, the interpreter path (never
the system Python when a venv exists), the data root, and any command that
was tried and froze the machine, in the do-not-run list.
