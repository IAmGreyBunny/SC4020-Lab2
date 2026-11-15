# Canonical-ID data preparation

The generator is [`shared_data.py`](../shared_data.py). It validates cleaning,
assigns dataset-wide numeric drug/protein IDs, and reproduces the existing Task 2
splits without changing pair membership, row order or original affinity tokens.

## Run from the repository root

Tested with Python 3.12.3 and the versions in [`requirements.txt`](../requirements.txt).
The generator itself needs NumPy and pandas; the remaining packages support
project analysis and notebooks.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m shared_data
```

To verify existing outputs without replacing them:

```bash
.venv/bin/python -m shared_data --check-only
```

The normal command creates missing outputs and verifies existing ones. It refuses
to overwrite inconsistent files. All data outputs can be regenerated from the
six input CSVs below. `--root PATH` supports a separate directory with the same
input layout.

## Required inputs

- `data/davis_all.csv`
- `data/kiba_all.csv`
- `data/davis_clean.csv` — validated DAVIS pKd values
- `data/kiba_clean.csv` — validated supplied transformed KIBA scores
- `data/davis_split_assignment.csv`
- `data/kiba_split_assignment.csv`

The compact assignment files store cleaned-row positions in original split
order, plus affinity-token overrides where older CSV serialization differs.
They preserve the existing approximately 70/15/15 warm-start split.

DAVIS is already pKd, so no second logarithmic conversion is applied.
`data/davis_clean.csv` is the single validated cleaned DAVIS input. The duplicate
Task 2 copy was removed. Missing KIBA observations are never zero-filled.

## Generated files

These are intentionally omitted from the submission branch and Git-ignored.
Run `python shared_data.py` before the notebooks or training runners to recreate
them. The six input CSVs above are the authoritative inputs and remain included.

| Files | Purpose |
|---|---|
| `data/{davis,kiba}_{drug,protein}_mapping.csv` | Four lookup tables linking canonical IDs to original SMILES/sequences |
| `data/{davis,kiba}_indexed.csv` | Two complete cleaned observation tables with canonical IDs |
| `data/splits/{davis,kiba}_{train,val,test}.csv` | Six original Task 2 partitions with canonical IDs added |
| `data/preparation_report.json` | Cleaning counts, preservation checks and hashes |

Indexed observation columns are:

```text
drug_id,protein_id,compound_iso_smiles,target_sequence,affinity
```

IDs are zero-based and assigned by sorting unique identities from each complete
cleaned dataset **before splitting**. Every task/partition must reuse these same
mappings. IDs are dataset-specific and are identifiers, not numerical features.

| Dataset | Cleaned pairs | Drugs | Proteins |
|---|---:|---:|---:|
| DAVIS | 25,772 | 68 | 379 |
| KIBA | 117,657 | 2,068 | 229 |

The generator verifies duplicate-free/disjoint partitions, complete pair
coverage, training coverage of evaluation entities and exact CSV cell
preservation. Raw mean-aggregation checks use absolute tolerance `1e-12` for
historical floating-point serialization differences, recorded in the report.
It performs no model fitting or test prediction.

All runtime datasets live under this folder. `splits/` holds the shared Task 2
partitions. `open_task/` holds generated embeddings, joint ID mappings and
cold-target splits; its IDs differ from the dataset-specific Task 2 IDs.
Those generated files are created by `open_task/prepare_data.ipynb` and ignored by Git.

Generation preserves the six original split CSVs byte-for-byte. Recorded
experiment provenance may retain paths from before the folder consolidation.
