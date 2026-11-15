"""Improved biased MF: a cold target borrows parameters from similar training proteins."""

import numpy as np

from utils.biased_mf import predict_biased_mf
from shared_data import DRUG, PROTEIN

# Five neighbours: one alone loses to the drug mean once the holdout passes 0.2, because the
# nearest remaining training protein drifts away as training shrinks; twenty-five dilutes the
# close ones at small holdouts. Fixed, not selected, so this adds no validation pass.
NEIGHBOURS = 5


def predict_improved_biased_mf(model, pairs, protein_ids, protein_vectors, trained_protein_ids,
                         baseline, k=NEIGHBOURS):
    """Biased MF predictions where a held-out target borrows its neighbours' parameters.

    A protein the model never trained on has no bias and no factors, which is why
    predict_biased_mf refuses it. Its sequence embedding exists regardless, so the k most
    similar training proteins lend theirs, averaged by cosine similarity, and biased MF's own
    formula runs on the result. Each cold target then gets its own prediction rather than one
    constant per drug, which is what lets the model rank a drug's unseen targets.

    pairs: renumbered drug_id and protein_id, the frame predict_biased_mf expects.
    protein_ids: the canonical protein id of each row, indexing protein_vectors.
    trained_protein_ids: the training proteins' canonical ids in ascending order. The holdout
        renumbering numbers training entities in that same order, so column i of the similarity
        matrix is the model's own target index i.
    baseline: the mean tier to keep wherever the drug itself is untrained and no drug bias
        exists to build on.

    Returns (predictions, fallback), fallback marking only the rows left on the baseline.
    """
    predictions = np.asarray(baseline, dtype=np.float64).copy()
    fallback = np.ones(len(predictions), dtype=bool)

    drug_index = pairs[DRUG].to_numpy()
    warm_drug = drug_index < len(model["drugs"])
    warm_protein = pairs[PROTEIN].to_numpy() < len(model["targets"])

    known = warm_drug & warm_protein
    predictions[known] = predict_biased_mf(model, pairs[known])
    fallback[known] = False

    borrow = warm_drug & ~warm_protein
    if borrow.any():
        unit = protein_vectors / np.linalg.norm(protein_vectors, axis=1, keepdims=True)
        similarity = unit[np.asarray(protein_ids)[borrow]] @ unit[trained_protein_ids].T

        neighbours = np.argsort(-similarity, axis=1)[:, :k]
        weights = np.take_along_axis(similarity, neighbours, axis=1)
        weights = weights / weights.sum(axis=1, keepdims=True)

        bias = (weights * model["target_bias"][neighbours]).sum(axis=1)
        factors = (weights[:, :, None] * model["target_factors"][neighbours]).sum(axis=1)

        drugs = drug_index[borrow]
        predictions[borrow] = (
            float(model["global_mean"]) + model["drug_bias"][drugs] + bias
            + np.einsum("ij,ij->i", model["drug_factors"][drugs], factors))
        fallback[borrow] = False

    return predictions, fallback
