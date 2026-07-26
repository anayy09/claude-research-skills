# Serving LLMs on a compute node

Contents:
1. Why serve instead of loading per batch
2. vLLM server job script
3. Waiting for readiness
4. Client configuration
5. Reaching the server from a login node or laptop
6. Concurrency and throughput
7. Determinism for ablations
8. Using an already-running institutional endpoint

---

## 1. Why serve instead of loading per batch

A 27B model takes minutes to load and tens of gigabytes of GPU memory. A prompt
ablation with five arms over 400k patches that loads the model per arm spends
most of its wall clock on initialization. Start the server once, run every arm
against it, then stop it. This also makes the arms directly comparable: identical
weights, identical runtime, identical kernel versions.

---

## 2. vLLM server job script

```bash
#!/bin/bash
#SBATCH --job-name=vllm-medgemma
#SBATCH --account=GROUP
#SBATCH --qos=GROUP
#SBATCH --partition=PARTITION
#SBATCH --nodes=1 --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=200gb
#SBATCH --gres=gpu:a100:2
#SBATCH --time=08:00:00
#SBATCH --output=logs/%x_%j.out

set -euo pipefail
module purge && module load conda
conda activate /blue/GROUP/$USER/envs/vllm

export HF_HOME=/blue/GROUP/$USER/.cache/huggingface
PORT=$(python - <<'EOF'
import socket
s = socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()
EOF
)
ENDPOINT_FILE=/blue/GROUP/$USER/endpoints/$SLURM_JOB_ID.json
mkdir -p "$(dirname "$ENDPOINT_FILE")"
cat > "$ENDPOINT_FILE" <<EOF
{"base_url": "http://$(hostname):${PORT}/v1", "job_id": "$SLURM_JOB_ID", "model": "$MODEL"}
EOF
echo "endpoint written to $ENDPOINT_FILE"

srun python -m vllm.entrypoints.openai.api_server \
  --model "$MODEL" \
  --served-model-name medgemma \
  --host 0.0.0.0 --port "$PORT" \
  --tensor-parallel-size 2 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --dtype bfloat16
```

Notes:

- Bind `0.0.0.0`, not `127.0.0.1`, or nothing outside the node can reach it.
- Pick a free port programmatically. A hardcoded port collides when two of your
  jobs share a node.
- Write the resolved URL to a file. The client reads that file rather than
  having the hostname pasted in by hand, which is the step that goes stale.
- Set `--max-model-len` explicitly. Leaving it at the model default can either
  reserve far more KV cache than needed or silently truncate long prompts.
- `--tensor-parallel-size` must equal the number of GPUs requested.
- If startup fails with a KV cache allocation error, lower
  `--gpu-memory-utilization` to 0.85 or reduce `--max-model-len`.

---

## 3. Waiting for readiness

Sending requests before the weights finish loading produces connection errors
that look like a broken server. Poll:

```bash
BASE=$(python -c "import json,sys;print(json.load(open(sys.argv[1]))['base_url'])" "$ENDPOINT_FILE")
for i in $(seq 1 120); do
  if curl -sf "${BASE%/v1}/health" > /dev/null; then echo "ready after ${i}0s"; break; fi
  sleep 10
done
curl -s "$BASE/models" | head -c 400
```

---

## 4. Client configuration

Any OpenAI-compatible client works. Point it at the endpoint file so nothing is
hardcoded:

```python
import json, os
from openai import OpenAI

ep = json.load(open(os.environ["ENDPOINT_FILE"]))
client = OpenAI(base_url=ep["base_url"], api_key="EMPTY")

resp = client.chat.completions.create(
    model="medgemma",
    messages=[{"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
    ]}],
    temperature=0.0,
    max_tokens=64,
    seed=0,
)
```

Record `ep["job_id"]`, the served model name, and the vLLM version in the run
manifest. Two runs against different server jobs are not automatically
comparable, and a silent server restart between arms is exactly the kind of
confound that survives review and then fails replication.

---

## 5. Reaching the server from a login node or laptop

From a login node, the compute node hostname usually resolves directly, so
`curl http://<node>:<port>/v1/models` works. From a laptop, tunnel:

```bash
ssh -N -L 8000:<compute-node>:<port> <user>@hpg.rc.ufl.edu
# then use http://localhost:8000/v1
```

Do not expose an inference endpoint that has processed clinical data to any
network path broader than necessary, and do not add an authentication bypass to
make a tunnel unnecessary.

---

## 6. Concurrency and throughput

vLLM batches continuously, so throughput comes from having many requests in
flight, not from large client-side batches. Use an async client with a bounded
semaphore:

```python
import asyncio
sem = asyncio.Semaphore(64)          # tune: start at 32, raise until latency degrades

async def one(item):
    async with sem:
        return await client.chat.completions.create(...)
```

Measure tokens per second from the vLLM log at two concurrency levels before
committing to a full sweep. Beyond a point, more concurrency raises latency
without raising throughput, and can trigger preemption of long requests.

Set client timeouts and retry with backoff on 5xx only. Retrying on a 400 loops
forever on a malformed prompt.

---

## 7. Determinism for ablations

Full determinism is not achievable across batch compositions with continuous
batching, because the batch a request lands in affects kernel reduction order.
Practical mitigations:

- `temperature=0.0` and a fixed `seed` for every arm.
- Record the exact prompt template hash per arm, not a description of it.
- Treat residual nondeterminism as measurement noise: rerun one arm twice and
  report the run-to-run difference alongside the between-arm difference. If they
  are the same size, the ablation has not shown anything.

That last check is cheap and it is the one most often skipped.

---

## 8. Using an already-running institutional endpoint

If the group already hosts an OpenAI-compatible endpoint on a persistent node,
prefer it over starting your own: no queue wait, no allocation spend. Query it
for the catalog rather than assuming which models are available:

```bash
curl -s http://<host>/v1/models | python -m json.tool
```

Record the model string exactly as returned, including any revision suffix.
Mixture-of-experts models report total parameters, not active parameters; when
comparing throughput or capability across such models, note both, since active
parameter count is what drives per-token compute.

Confirm the data handling terms of a shared endpoint before sending clinical
data through it. On-premises hosting is a necessary condition for that, not a
sufficient one.
