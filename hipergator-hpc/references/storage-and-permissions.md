# Storage, small files, and group permissions

Contents:
1. Choosing a filesystem
2. The small-file problem
3. Staging to node-local scratch
4. Group permissions and ACLs
5. Quota diagnosis
6. Data that must not move

---

## 1. Choosing a filesystem

| Path | Backing | Good for | Bad for |
|---|---|---|---|
| `/home/$USER` | small quota | shell config, source code, small scripts | conda envs, caches, data |
| `/blue/<group>` | parallel FS, high performance | active job I/O, checkpoints, intermediate artifacts | permanent archives |
| `/orange/<group>` | bulk, lower cost | source datasets, released results, sharing across the lab | high-IOPS random reads during training |
| `$TMPDIR` | node-local disk | unpacking archives, temporary shards, sqlite/duckdb working files | anything needed after the job ends |

Check actual quota usage before a large write. Filling `/blue` mid-run causes
corrupt checkpoints and confusing errors from libraries that do not check write
return codes:

```bash
blue_quota; orange_quota; home_quota      # UF RC wrappers
du -sh /blue/<group>/$USER/* | sort -h | tail -20
```

Redirect every cache away from `/home` in the job script:

```bash
export HF_HOME=/blue/GROUP/$USER/.cache/huggingface
export TORCH_HOME=/blue/GROUP/$USER/.cache/torch
export XDG_CACHE_HOME=/blue/GROUP/$USER/.cache
export PIP_CACHE_DIR=/blue/GROUP/$USER/.cache/pip
export TRITON_CACHE_DIR=$TMPDIR/triton
```

Conda environments belong on `/blue`, not `/home`. A single PyTorch environment
can exceed a home quota by itself:

```bash
conda create -p /blue/GROUP/$USER/envs/cpath python=3.11
conda activate /blue/GROUP/$USER/envs/cpath
```

---

## 2. The small-file problem

A parallel filesystem is optimized for a modest number of large files. A
histopathology patch pipeline naturally produces the opposite: hundreds of
thousands of small PNGs. Symptoms are a job that is neither CPU nor GPU bound,
a dataloader that stalls, and metadata operations (`ls`, `du`) that take minutes.

It also degrades the filesystem for everyone else on the cluster, which is a
good reason to fix it beyond your own throughput.

Three fixes, in order of preference:

1. **Do not write patches to disk at all.** Tile on the fly from the WSI with
   OpenSlide inside the dataloader. Costs CPU, eliminates the problem entirely,
   and removes a whole preprocessing stage from the pipeline.
2. **Shard.** Pack patches into WebDataset tars or Parquet with the image bytes
   in a binary column, roughly 200 MB to 1 GB per shard, then read sequentially.
3. **Archive and stage.** Keep one tar per slide on `/orange`, copy and unpack
   into `$TMPDIR` at job start.

Rough targets: aim for thousands of files per directory, not millions, and
average file size in the megabytes rather than the kilobytes.

---

## 3. Staging to node-local scratch

```bash
STAGE=$TMPDIR/data
mkdir -p "$STAGE"
echo "staging $(date)"
tar -xf /orange/GROUP/datasets/nct-crc-he-100k.tar -C "$STAGE"
echo "staged $(date), $(du -sh $STAGE)"

srun python -u train.py --data "$STAGE" --out /blue/GROUP/$USER/runs/$SLURM_JOB_ID
# $TMPDIR is cleaned automatically when the job exits; copy out anything you need first
```

Stage once per job, not once per epoch. If the copy takes longer than the
compute, the job is too small to be worth a separate submission and should be
merged into an array task with more work per task.

---

## 4. Group permissions and ACLs

The recurring failure: user A writes results under a shared project directory
with a personal umask, user B cannot read them, and the fix is applied file by
file after the fact. Fix the directory once instead.

```bash
PROJ=/orange/<group>/<project>

chgrp -R <group> "$PROJ"
chmod -R g+rwX "$PROJ"          # capital X: execute on directories only
chmod g+s "$PROJ"               # setgid: new entries inherit the group

# Default ACL so files created later are group-writable without further action
setfacl -R  -m g:<group>:rwX "$PROJ"
setfacl -R -d -m g:<group>:rwX "$PROJ"

getfacl "$PROJ"                 # verify: look for the default: lines
```

Then set `umask 007` in the job script (or in `~/.bashrc` if every project is
group-shared) so the process itself does not strip group bits.

For a released, read-only dataset that should not be modified after curation:

```bash
setfacl -R  -m g:<group>:rX  "$PROJ"
setfacl -R -d -m g:<group>:rX "$PROJ"
```

Diagnosing a `Permission denied` that looks impossible: check every component of
the path, not just the leaf. A directory missing group execute blocks access to
everything beneath it regardless of the permissions on the files.

```bash
namei -l /orange/<group>/<project>/subdir/file.parquet
```

`namei -l` prints the ownership and mode of each path component and immediately
shows which level is wrong.

---

## 5. Quota diagnosis

Two separate limits exist: bytes and file count (inodes). A pipeline that
produced a million patch files can exhaust the inode quota while using a small
fraction of the byte quota, which produces "disk quota exceeded" on a filesystem
that appears mostly empty.

```bash
blue_quota                       # shows both if available
find /blue/GROUP/$USER -xdev -type f | wc -l          # slow but definitive
find /blue/GROUP/$USER -xdev -type d -printf '%h\n' | sort | uniq -c | sort -rn | head
```

The second command finds the directories holding the most entries, which is
almost always the unsharded patch cache.

---

## 6. Data that must not move

Restricted clinical data (MIMIC derivatives, PHI-containing extracts, IRB-scoped
cohorts) has an approved storage location and an approved processing boundary.
Before copying such data to `$TMPDIR`, to a personal directory, or off cluster,
confirm the destination is inside that boundary. Node-local scratch is generally
inside it; a laptop, a personal cloud drive, and an external API endpoint are
not.

When in doubt, keep the data where it is and move the computation to it. That is
what the cluster is for.
