# Storage, scratch, and group permissions

Contents:
1. Choosing a filesystem
2. The small-file problem
3. Staging to node-local scratch
4. Group permissions and ACLs
5. Quota and inode diagnosis
6. Purge policies
7. Data that must not move

---

## 1. Choosing a filesystem

Sites name their filesystems differently — `/scratch`, `/work`, `/projects`,
`/lustre`, `/gpfs`, `/nobackup`, or a group path under a local mount. The names
vary; the roles do not. Identify which local path plays each role once, assign it
to a variable, and write job scripts against the variable.

| Role | Typical variable | Backing | Good for | Bad for |
|---|---|---|---|---|
| Home | `$HOME` | small quota, backed up | shell config, source code, small scripts | environments, caches, data |
| Fast parallel scratch | `$SCRATCH`, `$WORK` | parallel FS (Lustre, GPFS, BeeGFS) | active job I/O, checkpoints, intermediate artifacts | anything irreplaceable, if it is purged |
| Bulk / project | `$PROJECT`, `$ARCHIVE` | bulk, lower cost, sometimes tape-backed | source datasets, released results, sharing across the group | high-IOPS random reads during training |
| Node-local scratch | `$TMPDIR`, `$SLURM_TMPDIR` | local SSD or NVMe | unpacking archives, temporary shards, sqlite/duckdb working files | anything needed after the job ends |

A few sites give compute nodes no local disk at all, in which case `$TMPDIR` is a
RAM-backed tmpfs that counts against `--mem`. Check with `df -h "$TMPDIR"` inside
an interactive job before designing a pipeline around staging.

Check actual quota usage before a large write. Filling a filesystem mid-run
produces corrupt checkpoints and confusing errors from libraries that do not
check write return codes:

```bash
quota -s 2>/dev/null                     # if the site uses standard quotas
lfs quota -h -u "$USER" /scratch         # Lustre
mmlsquota --block-size auto              # GPFS
du -sh "$WORK"/* | sort -h | tail -20
```

Sites frequently ship their own quota wrapper instead. Look for it in the login
banner or the user guide rather than guessing a name.

Redirect every cache away from `$HOME` in the job script:

```bash
export HF_HOME="$WORK/.cache/huggingface"
export TORCH_HOME="$WORK/.cache/torch"
export XDG_CACHE_HOME="$WORK/.cache"
export PIP_CACHE_DIR="$WORK/.cache/pip"
export TRITON_CACHE_DIR="${TMPDIR:-/tmp}/triton"
```

Python environments belong on a project or scratch filesystem, not in `$HOME`. A
single PyTorch environment can exceed a home quota by itself:

```bash
python -m venv "$WORK/venv" && source "$WORK/venv/bin/activate"
# or, with conda:
conda create -p "$WORK/envs/myenv" python=3.11
conda activate "$WORK/envs/myenv"
```

Environments made of tens of thousands of small files are also slow to load from
a parallel filesystem. If job startup is dominated by imports, pack the
environment into a container image or a squashfs and mount it instead.

---

## 2. The small-file problem

A parallel filesystem is optimized for a modest number of large files. Many
research pipelines produce the opposite: hundreds of thousands of image tiles,
per-sample JSON files, individual audio clips, or one output file per simulation
step. Symptoms are a job that is neither CPU nor GPU bound, a dataloader that
stalls, and metadata operations (`ls`, `du`) that take minutes.

It also degrades the filesystem for everyone else on the cluster, which is a good
reason to fix it beyond your own throughput. Sustained metadata hammering is one
of the few things that will get an account suspended.

Three fixes, in order of preference:

1. **Do not write the small files at all.** Generate the units on the fly inside
   the dataloader from the source artifact. Costs CPU, eliminates the problem
   entirely, and removes a whole preprocessing stage from the pipeline.
2. **Shard.** Pack records into WebDataset tars, TFRecord, or Parquet with the
   binary payload in a column, roughly 200 MB to 1 GB per shard, then read
   sequentially.
3. **Archive and stage.** Keep one tar per group on the bulk filesystem, copy and
   unpack it into node-local scratch at job start.

Rough targets: thousands of files per directory, not millions, and average file
size in the megabytes rather than the kilobytes.

---

## 3. Staging to node-local scratch

```bash
STAGE="${TMPDIR:-/tmp}/data"
mkdir -p "$STAGE"
echo "staging $(date -Is)"
tar -xf "$DATA/dataset.tar" -C "$STAGE"
echo "staged $(date -Is), $(du -sh "$STAGE")"

srun python -u train.py --data "$STAGE" --out "$WORK/runs/$SLURM_JOB_ID"
# node-local scratch is cleaned when the job exits; copy out anything you need first
```

Stage once per job, not once per epoch. If the copy takes longer than the
compute, the job is too small to be worth a separate submission and should be
merged into an array task with more work per task.

For a multi-node job, every node needs its own copy — stage inside `srun` with
`--ntasks-per-node=1` rather than once in the batch script, or the ranks on other
nodes will find an empty directory.

---

## 4. Group permissions and ACLs

The recurring failure: user A writes results under a shared project directory
with a personal umask, user B cannot read them, and the fix is applied file by
file after the fact. Fix the directory once instead.

```bash
PROJ=/path/to/shared/project

chgrp -R GROUP "$PROJ"
chmod -R g+rwX "$PROJ"          # capital X: execute on directories only
chmod g+s "$PROJ"               # setgid: new entries inherit the group

# Default ACL so files created later are group-writable without further action
setfacl -R  -m g:GROUP:rwX "$PROJ"
setfacl -R -d -m g:GROUP:rwX "$PROJ"

getfacl "$PROJ"                 # verify: look for the default: lines
```

Then set `umask 007` in the job script (or in `~/.bashrc` if every project is
group-shared) so the process itself does not strip group bits.

For a released, read-only dataset that should not be modified after curation:

```bash
setfacl -R  -m g:GROUP:rX  "$PROJ"
setfacl -R -d -m g:GROUP:rX "$PROJ"
```

Not every parallel filesystem exposes POSIX ACLs. If `setfacl` returns
`Operation not supported`, setgid plus a group-friendly umask is the fallback;
create a test file afterwards and check its mode rather than assuming it worked.

Diagnosing a `Permission denied` that looks impossible: check every component of
the path, not just the leaf. A directory missing group execute blocks access to
everything beneath it regardless of the permissions on the files.

```bash
namei -l /path/to/shared/project/subdir/file.parquet
```

`namei -l` prints the ownership and mode of each path component and immediately
shows which level is wrong.

---

## 5. Quota and inode diagnosis

Two separate limits exist: bytes and file count (inodes). A pipeline that
produced a million small files can exhaust the inode quota while using a small
fraction of the byte quota, which produces "disk quota exceeded" on a filesystem
that appears mostly empty.

```bash
lfs quota -h -u "$USER" /scratch                      # Lustre: shows both
mmlsquota --block-size auto                           # GPFS
find "$WORK" -xdev -type f | wc -l                    # slow but definitive
find "$WORK" -xdev -type d -printf '%h\n' | sort | uniq -c | sort -rn | head
```

The last command finds the directories holding the most entries, which is almost
always the unsharded output cache.

On Lustre, also check whether one OST is full while the filesystem as a whole is
not (`lfs df -h`); a single huge file striped onto one target can fail to extend
even with space elsewhere.

---

## 6. Purge policies

Fast scratch is usually purged on file age — 30, 60, or 90 days since last
access, applied without warning and without a backup. Two consequences:

- Anything you would be upset to lose belongs on the project or archive
  filesystem, or off the cluster, before the window closes.
- `touch`-ing files to defeat the purge is against policy at most sites and is
  detectable. Move the data instead.

Find out the site's actual window, then make the copy-out step part of the last
job in a dependency chain rather than something you remember to do later.

---

## 7. Data that must not move

Restricted data — human subjects data, clinical extracts, data under a DUA, an
IRB-scoped cohort, export-controlled material — has an approved storage location
and an approved processing boundary. Before copying it to node-local scratch, to
a personal directory, or off the cluster, confirm the destination is inside that
boundary. Node-local scratch is generally inside it; a laptop, a personal cloud
drive, and an external API endpoint are not.

Some sites run a separate enclave for this class of data with its own login
nodes and no outbound network. Do not attempt to bridge the two.

When in doubt, keep the data where it is and move the computation to it. That is
what the cluster is for.
