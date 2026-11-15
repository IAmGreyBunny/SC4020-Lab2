# SC4020 Project 2: reproducible submission

This branch contains the active code and inputs for all three tasks. Notebook
outputs are retained for inspection. Generated CSVs, plots, embeddings and Task 3
models are recreated by the workflow below and are excluded from version control.

## Setup

Use Python 3.12 and run these commands from the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export PATH="$PWD/.venv/bin:$PATH"
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
```

On Windows, activate `.venv\Scripts\activate` instead and set the two thread
variables in your shell. Select this environment's Python kernel when using
Jupyter interactively. The environment includes Jupyter's execution tools;
an interactive Jupyter interface may be installed separately if needed.

Task 3 downloads pretrained encoders from Hugging Face on its first run and
generates embeddings locally. It uses CUDA when available, otherwise CPU.
Embedding generation and training take substantially longer than Tasks 1 and 2.
Allow disk space for the Python environment, downloaded models and generated
artifacts. Numerical results from neural-network retraining can vary with device
and library versions; the notebook outputs record the original experiment.

## Run order

Run each notebook from top to bottom, in the order below. The shell commands
execute it and refresh its saved outputs. `timeout=-1` permits the complete
embedding/training stages to finish.

### 1. Shared data

```bash
python shared_data.py
python shared_data.py --check-only
```

The six input CSVs in `data/` regenerate mappings, indexed data and the fixed
warm-start splits in `data/splits/`. Pair membership, ordering and affinity tokens
are preserved. See [data/README.md](data/README.md).

### 2. Task 1: dataset analysis

```bash
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 dataset-analysis.ipynb
```

Produces `outputs/` tables and `figures/` plots. Existing validated cleaned CSVs
are checked rather than overwritten.

### 3. Task 2: saved-model review

```bash
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 task2/task2.ipynb
python -m unittest discover -s task2/tests -p 'test*.py' -v
```

Loads the eight included Task 2 checkpoints and recomputes all model metrics and
six cases. Its 48-setting KNN search and 73-fit MF study are recorded evidence,
not new training runs. Results are written under
`task2/results/task2_submission/review/`. The compact published
[metrics CSV](task2/results/train_validation_test_metrics.csv) is also included.
Independent refitting commands are in [task2/README.md](task2/README.md).

### 4. Task 3: cold-target reproduction

Keep the notebook configuration defaults for a full reproduction:

```bash
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 open_task/prepare_data.ipynb
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 open_task/train_predictor.ipynb
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 open_task/CF_baselines.ipynb
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 open_task/evaluation.ipynb
```

Preparation downloads `DeepChem/ChemBERTa-100M-MLM` and
`facebook/esm2_t6_8M_UR50D`, using the revisions pinned in the notebook. It creates
joint drug/protein mappings, frozen embeddings and holdouts under `data/open_task/`.
These joint IDs differ from Task 2's dataset-specific IDs.

The predictor and CF notebooks train on each dataset at target holdouts
0, 0.1, 0.2, 0.3, 0.5 and 0.75. Validation and test pairs stay fixed across those
ratios; selected proteins are removed from training. Checkpoints go to
`open_task/models/saved_models/`, baseline predictions to `open_task/predictions/`,
and evaluation figures to `open_task/figures/`. No pre-existing Task 3 weights or
embedding files are required.

The Task 3 evaluation imports Task 2's metric definitions, with its documented
candidate-eligibility filters, and also reports within-drug CI. Keep `task2/utils/`
and the Task 2 MF checkpoints when packaging the whole project.

## Included and regenerated material

- Included: six source data CSVs; active notebooks and model implementations;
  Task 2 production checkpoints; MF tests; dependency pins; the Task 2 metrics CSV.
- Regenerated: indexed datasets and splits, analysis tables/figures, Task 2 review
  outputs, Task 3 embeddings, checkpoints and predictions.
- The report and video are separate group deliverables. Report drafts, old
  notebooks, the assignment PDF and duplicated generated exports are omitted.

Only the `submission` branch is cleaned; the original material remains on `main`
and in repository history.

## Reproduction checks

The complete workflow was executed in a fresh Python 3.12.3 environment using
the pinned requirements on Linux with an NVIDIA RTX 3050 Laptop GPU (4 GiB).
The six source CSVs and all included Task 2 checkpoints remained unchanged.

- All 13 generated shared-data files matched the original files byte-for-byte.
- Task 1 completed all 15 code cells and regenerated seven tables. Their numeric
  values matched the prior exports within `1e-12`; an obsolete duplicate coverage
  export is represented by `coverage_statistics.csv`.
- Task 2 completed all 16 code cells. Its 24-row metrics CSV matched exactly, as
  did the six case summaries and eight checkpoint reload checks. All 18 MF tests
  passed. The MF runner's prepare and smoke stages also passed independently.
- Task 3 generated 2,127 drug vectors and 429 protein vectors, verified all 12
  holdout conditions, trained 12 predictors and 48 baseline states, and generated
  120 baseline prediction files. Its evaluation completed with 680 measurement
  rows. Reloaded predictor validation scores matched their best training-history
  epochs. At zero holdout, the four shared baselines reproduced Task 2's MSE, CI
  and candidate-restricted Hit@5 within `1e-12` for all 16 comparisons.

Measured Task 3 stage times were approximately 1.2 minutes for preparation,
36.4 minutes for predictor training, 7.1 minutes for CF baselines and 4.5 minutes
for evaluation. Download, CPU-only and other hardware timings will differ.

### Original versus reproduced predictor results

Saved notebook outputs retain the original experiment. The fresh neural-network
training run completed successfully but did not reproduce those scores exactly.
The comparison below uses the original printed validation MSE (four decimals)
and the new run with the pinned environment; no results were adjusted to match.

| Dataset | Target holdout | Original validation MSE | Reproduced validation MSE |
|---|---:|---:|---:|
| DAVIS | 0.0 | 0.3476 | 0.3581 |
| DAVIS | 0.1 | 0.3768 | 0.3661 |
| DAVIS | 0.2 | 0.3665 | 0.3975 |
| DAVIS | 0.3 | 0.4028 | 0.4040 |
| DAVIS | 0.5 | 0.4145 | 0.4133 |
| DAVIS | 0.75 | 0.4635 | 0.4618 |
| KIBA | 0.0 | 0.2822 | 0.2926 |
| KIBA | 0.1 | 0.2557 | 0.2797 |
| KIBA | 0.2 | 0.3198 | 0.2909 |
| KIBA | 0.3 | 0.3288 | 0.3265 |
| KIBA | 0.5 | 0.3533 | 0.3644 |
| KIBA | 0.75 | 0.4451 | 0.4473 |

The largest observed absolute difference was about 0.0310. The model algorithms,
data partitions and training settings were preserved. This verifies a complete
retraining/evaluation workflow, rather than exact recovery of the original neural
weights. Use results generated together in one run when making model comparisons.
