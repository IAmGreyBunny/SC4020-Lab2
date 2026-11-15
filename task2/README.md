# Task 2: warm-start affinity prediction

Open [`task2.ipynb`](task2.ipynb) and Run All after installing the root
[`requirements.txt`](../requirements.txt). The notebook prepares the shared
canonical data if needed, loads eight saved models and recomputes training,
validation and test metrics, checkpoint reload checks and six fixed cases.
It does not retrain models.

The implementations are in `utils/`: Global Mean, Protein CF, Drug CF, Biased MF
and shared evaluation functions. Production states are in `saved_models/`.
Task 3 also imports these modules and reads the two MF checkpoints.

## Results and experiment evidence

[`results/train_validation_test_metrics.csv`](results/train_validation_test_metrics.csv)
contains the 24 verified evaluation rows. See the [column guide](results/README.md).
Run All regenerates it with the plots, full candidate rankings and checkpoint
copies under `results/task2_submission/review/`, which is Git-ignored.

The notebook embeds the 48-setting KNN search, the five-stage 73-fit MF campaign
and all 3,275 epoch rows. It also retains two historical lambda=100 results,
separately labelled and excluded from selection. No external experiment tables,
old notebooks or pre-generated images are needed.

## Tests

From the repository root, after generating the shared data:

```bash
python -m unittest discover -s task2/tests -p 'test*.py' -v
```

## Deliberate training reproduction

First run `python shared_data.py` to create mappings and splits. Use a new output
directory so existing checkpoints remain intact.

```bash
python -m task2.run_models --knn-search --output-dir .local_artifacts/model_refit

OUT=.local_artifacts/mf_reproduction
python -m task2.run_biased_mf --stage prepare --output-dir "$OUT"
python -m task2.run_biased_mf --stage tests --output-dir "$OUT"
for STAGE in capacity interaction rates seeds summarize verify; do
  python -m task2.run_biased_mf --stage "$STAGE" --output-dir "$OUT" || break
done
```

These runners fit on training data and use validation for selection. They are
separate from the checkpoint-review notebook. Full project execution order and
Task 3 reproduction are documented in the root [README](../README.md).
