"""Run weighted random walk with restart on a PPI network."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx


def read_seeds(path: Path) -> list[str]:
    if path.suffix.lower() == ".txt":
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return pd.read_csv(path).iloc[:, 0].astype(str).tolist()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--seeds", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--restart-prob", type=float, default=0.5)
    parser.add_argument("--max-iter", type=int, default=100)
    parser.add_argument("--tol", type=float, default=1.0e-6)
    args = parser.parse_args()
    table = pd.read_csv(args.input)
    table[["Gene_ID_1", "Gene_ID_2"]] = table[["Gene_ID_1", "Gene_ID_2"]].astype(str)
    graph = nx.from_pandas_edgelist(table, "Gene_ID_1", "Gene_ID_2", edge_attr="final_weight")
    nodes = list(graph.nodes())
    index = {node: i for i, node in enumerate(nodes)}
    matrix = nx.to_numpy_array(graph, nodelist=nodes, weight="final_weight", dtype=float)
    column_sum = matrix.sum(axis=0)
    column_sum[column_sum == 0] = 1.0
    transition = matrix / column_sum
    seeds = [seed for seed in read_seeds(args.seeds) if seed in index]
    if not seeds:
        raise ValueError("No seed genes are present in the network")
    initial = np.zeros(len(nodes), dtype=float)
    initial[[index[seed] for seed in seeds]] = 1.0 / len(seeds)
    scores = initial.copy()
    for _ in range(args.max_iter):
        updated = (1 - args.restart_prob) * transition.dot(scores) + args.restart_prob * initial
        if np.linalg.norm(updated - scores, ord=1) < args.tol:
            scores = updated
            break
        scores = updated
    result = pd.DataFrame({"Gene_ID": nodes, "RWR_score": scores}).sort_values("RWR_score", ascending=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"saved RWR scores -> {args.output}")


if __name__ == "__main__":
    main()

