# Matplotlib recipes for manuscript figures

House style in practice. Every recipe assumes the setup block; adjust data
variables, keep the structure.

## Contents

1. [Setup](#setup)
2. [Sizing and panels](#sizing-and-panels)
3. [Recipes](#recipes)
   - Line with uncertainty band
   - Grouped bars with error bars
   - Box + strip (small-n distributions)
   - Heatmap with colorbar
   - ROC / PR curves
   - Calibration (reliability) plot
   - Forest plot
   - Confusion matrix
   - Training curves
4. [Export](#export)
5. [Common fixes](#common-fixes)

## Setup

```python
import sys
sys.path.insert(0, "path/to/manuscript-figures/scripts")  # or copy figstyle.py into the project
import figstyle
import matplotlib.pyplot as plt
import numpy as np

figstyle.apply_style()            # fonts, sizes, spines, Okabe-Ito cycle, fonttype 42
C = figstyle.OKABE_ITO            # dict: C["blue"], C["vermillion"], ...
```

`apply_style()` accepts `base_size` (default 7) and `font` overrides. Without
the module, `plt.style.use("assets/manuscript.mplstyle")` gives the same
rcParams.

## Sizing and panels

```python
# Single-column figure, golden ratio height
fig, ax = plt.subplots(figsize=figstyle.fig_size("single", journal="elsevier"),
                       layout="constrained")

# Exact LaTeX width (user compiled \the\columnwidth -> 243.9pt)
fig, ax = plt.subplots(figsize=figstyle.fig_size(width_mm=243.9 / 72.27 * 25.4))

# Multi-panel, double column: mosaic gives named panels and uneven layouts
fig = plt.figure(figsize=figstyle.fig_size("double", journal="nature", aspect=0.45),
                 layout="constrained")
axs = fig.subplot_mosaic([["a", "b", "b"],
                          ["c", "c", "d"]])
figstyle.label_panels(axs)        # bold a, b, c, d outside top-left corners
```

Rules that keep panels publishable:

- One `figsize` decision at the top, in final printed mm, then never scale.
- `layout="constrained"` instead of `tight_layout()`; it respects the declared
  size.
- Shared quantities share axes: `sharey=True` across comparable panels, drop
  interior labels (`ax.set_ylabel("")` on non-left panels).
- Interior panel ticks: keep the ticks, drop the tick *labels*.

## Recipes

### Line with uncertainty band

For anything vs. a continuous variable (epochs, dose, threshold) with
seed/fold variation.

```python
x = np.arange(1, 51)
for name, runs in results.items():           # runs: (n_seeds, len(x))
    m, s = runs.mean(0), runs.std(0)
    lo, hi = m - 1.96 * s / np.sqrt(len(runs)), m + 1.96 * s / np.sqrt(len(runs))
    line, = ax.plot(x, m, label=name)
    ax.fill_between(x, lo, hi, color=line.get_color(), alpha=0.18, lw=0)
ax.set_xlabel("Epoch"); ax.set_ylabel("Validation AUROC")
ax.legend()
```

Caption must state what the band is (here, 95% CI of the mean over seeds).
Bands, not error bars, for dense x; never both.

### Grouped bars with error bars

Only for quantities where zero is meaningful. Otherwise use the box+strip
recipe.

```python
groups, methods = ["A", "B", "C"], list(scores)   # scores[m]: (n_groups,) means
xpos = np.arange(len(groups)); w = 0.8 / len(methods)
for i, m in enumerate(methods):
    ax.bar(xpos + i * w, scores[m], width=w, label=m,
           yerr=errs[m], capsize=2, error_kw={"lw": 0.8})
ax.set_xticks(xpos + w * (len(methods) - 1) / 2, groups)
ax.set_ylabel("Dice score"); ax.set_ylim(0, 1); ax.legend()
```

No 3D, no shadows, no per-bar value labels unless the venue's readership
expects them; the y-axis already encodes the value.

### Box + strip (small-n distributions)

The honest default when n per group is under ~30.

```python
data = [vals_a, vals_b, vals_c]
bp = ax.boxplot(data, widths=0.5, showfliers=False, patch_artist=True,
                medianprops={"color": "black", "lw": 1.0},
                boxprops={"facecolor": "none", "lw": 0.8},
                whiskerprops={"lw": 0.8}, capprops={"lw": 0.8})
rng = np.random.default_rng(0)
for i, vals in enumerate(data, start=1):
    ax.plot(rng.normal(i, 0.06, len(vals)), vals, "o", ms=2.2,
            alpha=0.6, mew=0, color=C["blue"])
ax.set_xticklabels(["A", "B", "C"]); ax.set_ylabel("Latency (ms)")
```

### Heatmap with colorbar

```python
im = ax.imshow(M, cmap="viridis", aspect="auto",
               vmin=vmin, vmax=vmax)               # fix limits explicitly
cb = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
cb.set_label("Attention weight")                    # a colorbar always has a label
ax.set_xticks(range(len(cols)), cols, rotation=45, ha="right")
ax.set_yticks(range(len(rows)), rows)
```

Diverging data: `cmap="RdBu_r"` with `norm=matplotlib.colors.CenteredNorm()`
(or `TwoSlopeNorm`) so the midpoint sits at the meaningful zero. Large
heatmaps may rasterize the mesh only: `im.set_rasterized(True)` keeps text
vector while capping file size.

### ROC / PR curves

```python
fig, ax = plt.subplots(figsize=figstyle.fig_size("single", aspect=1.0),
                       layout="constrained")
for name, (fpr, tpr, auc) in curves.items():
    ax.plot(fpr, tpr, label=f"{name} (AUROC {auc:.3f})")
ax.plot([0, 1], [0, 1], ls="--", lw=0.6, color="0.5", zorder=0)
ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect("equal")
ax.legend(loc="lower right")
```

Report AUROC in the legend with a CI when available (see the
`ml-eval-statistics` skill for computing it properly). For imbalanced tasks,
pair with a PR curve; the PR no-skill line is the prevalence, not the
diagonal.

### Calibration (reliability) plot

```python
ax.plot([0, 1], [0, 1], ls="--", lw=0.6, color="0.5")
ax.plot(bin_conf, bin_acc, "o-", ms=3)
ax.set_xlabel("Predicted probability"); ax.set_ylabel("Observed frequency")
ax.set_aspect("equal"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
# Sample-count histogram as a small twin below or inset, so empty bins are visible
```

### Forest plot

For per-subgroup effects with CIs; standard in clinical work.

```python
y = np.arange(len(labels))[::-1]
ax.errorbar(est, y, xerr=np.abs(ci - est[:, None]).T, fmt="s", ms=3,
            capsize=2, lw=0.9, color="black")
ax.axvline(ref_value, ls="--", lw=0.6, color="0.5")   # 1.0 for ratios, 0 for differences
ax.set_yticks(y, labels)
ax.set_xlabel("Odds ratio (95% CI)")
ax.set_xscale("log")                                   # ratios live on log axes
```

### Confusion matrix

```python
im = ax.imshow(cm_norm, cmap="Blues", vmin=0, vmax=1)
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, f"{cm[i, j]:d}", ha="center", va="center", fontsize=6,
                color="white" if cm_norm[i, j] > 0.55 else "black")
ax.set_xticks(range(k), classes, rotation=45, ha="right")
ax.set_yticks(range(k), classes)
ax.set_xlabel("Predicted"); ax.set_ylabel("True")
```

State in the caption whether cells are counts or row-normalized rates.

### Training curves

Loss/metric vs. steps for multiple runs: use the uncertainty-band recipe. Two
additions: log-scale the y-axis for losses spanning decades, and if smoothing
is applied, plot the raw curve at `alpha=0.25` under the smoothed one and say
so in the caption. A smoothed-only curve misrepresents variance.

## Export

```python
figstyle.save_figure(fig, "figures/fig2_ablation")
# -> fig2_ablation.pdf (vector, fonts embedded) + fig2_ablation.png (600 dpi)
figstyle.save_figure(fig, "figures/fig2_ablation", formats=("pdf", "png", "tif"))
```

`save_figure` writes without `bbox_inches="tight"` by design: the figure was
built at the declared size, and tight-cropping would change it. If something
is clipped, fix the layout, not the crop.

Then verify:

```bash
python scripts/check_figure.py figures/fig2_ablation.pdf --journal elsevier --width single
```

## Common fixes

- **Fonts look different in the PDF** → a serif math font leaked in. Keep
  math minimal or set `mathtext.fontset: dejavusans` (apply_style does).
- **Text turned into curves in the PDF** → something set `pdf.fonttype: 3`.
  `apply_style()` forces 42; re-apply after any `plt.style.use`.
- **Huge PDF from a dense scatter/heatmap** → rasterize the artist only:
  `artist.set_rasterized(True)` and save with `dpi=600`. Text stays vector.
- **Legend covers data** → move it out: `ax.legend(loc="upper left",
  bbox_to_anchor=(1.01, 1))` or above the axes with `ncols=len(handles)`.
- **Rotated tick labels clipped** → `rotation=45, ha="right"` plus
  constrained layout, not manual bottom margins.
- **Panels differ in axis ranges for the same quantity** → set shared
  `xlim/ylim` explicitly; reviewers read across panels.
- **Colors fine on screen, mud in print** → run the grayscale test:
  `np.dot(rgb, [0.299, 0.587, 0.114])`; re-space lightness or add
  linestyle/marker redundancy.
