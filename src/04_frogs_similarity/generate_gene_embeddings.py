"""Study-specific wrapper for generating gene vectors from FRoGS embeddings.

The FRoGS model and pretrained embeddings are third-party resources. This
script only prepares the selected gene list and writes a reproducible output.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize


def load_embeddings(path: Path) -> dict[str, np.ndarray]:
    result: dict[str, np.ndarray] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if len(row) < 2:
                continue
            try:
                vector = np.asarray(row[1:], dtype=np.float32)
            except ValueError:
                continue  # optional header
            result[str(row[0])] = vector
    if not result:
        raise ValueError(f"No numeric embeddings found in {path}")
    return result


def similarity_stats(embedding: dict[str, np.ndarray]) -> dict[str, tuple[float, float]]:
    ids = list(embedding)
    matrix = normalize(np.vstack([embedding[i] for i in ids]))
    similarities = cosine_similarity(matrix, matrix)
    return {gene: (float(similarities[i].mean()), float(similarities[i].std())) for i, gene in enumerate(ids)}


def signature_vector(gene_ids: list[str], go: dict[str, np.ndarray], archs4: dict[str, np.ndarray], go_stats, arch_stats) -> np.ndarray:
    go_dim = len(next(iter(go.values())))
    arch_dim = len(next(iter(archs4.values())))
    go_matrix = normalize(np.vstack([go.get(gene, np.zeros(go_dim)) for gene in gene_ids]))
    arch_matrix = normalize(np.vstack([archs4.get(gene, np.zeros(arch_dim)) for gene in gene_ids]))

    def weights(matrix, stats, genes):
        pairwise = cosine_similarity(matrix, matrix)
        means = np.array([stats.get(gene, (0.0, 1.0))[0] for gene in genes])
        stds = np.array([stats.get(gene, (0.0, 1.0))[1] for gene in genes])
        stds[stds == 0] = np.inf
        return (pairwise.mean(axis=1) - means) / stds

    weight = np.maximum(weights(go_matrix, go_stats, gene_ids), weights(arch_matrix, arch_stats, gene_ids))
    weight = np.clip(np.nan_to_num(weight, nan=0.0), 0.0, 1.0).reshape(-1, 1)
    combined = np.hstack([go_matrix, arch_matrix])
    denominator = max(float(weight.sum()), 1e-100)
    return np.sum(combined * weight, axis=0) / denominator


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gene-list", type=Path, required=True)
    parser.add_argument("--go-embeddings", type=Path, required=True)
    parser.add_argument("--archs4-embeddings", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    genes = [line.strip() for line in args.gene_list.read_text(encoding="utf-8").splitlines() if line.strip()]
    go, archs4 = load_embeddings(args.go_embeddings), load_embeddings(args.archs4_embeddings)
    go_stats, arch_stats = similarity_stats(go), similarity_stats(archs4)
    vectors = {gene: signature_vector([gene], go, archs4, go_stats, arch_stats) for gene in genes if gene in go or gene in archs4}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        dimension = len(next(iter(vectors.values()))) if vectors else 0
        writer.writerow(["Gene_ID"] + [f"Feature_{i + 1}" for i in range(dimension)])
        for gene, vector in vectors.items():
            writer.writerow([gene] + vector.tolist())
    print(f"saved {len(vectors)} vectors -> {args.output}")


if __name__ == "__main__":
    main()

