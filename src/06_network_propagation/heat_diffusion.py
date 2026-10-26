"""Run heat diffusion on a weighted PPI network."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx
from scipy.linalg import expm


def read_seeds(path: Path) -> list[str]:
    if path.suffix.lower() == ".txt":
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return pd.read_csv(path).iloc[:, 0].astype(str).tolist()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--seeds", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--time", type=float, default=0.1)
    args = parser.parse_args()
    table = pd.read_csv(args.input)
    table[["Gene_ID_1", "Gene_ID_2"]] = table[["Gene_ID_1", "Gene_ID_2"]].astype(str)
    graph = nx.from_pandas_edgelist(table, "Gene_ID_1", "Gene_ID_2", edge_attr="final_weight")
    nodes = list(graph.nodes())
    adjacency = nx.to_numpy_array(graph, nodelist=nodes, weight="final_weight", dtype=float)
    laplacian = np.diag(adjacency.sum(axis=1)) - adjacency
    seed_set = set(read_seeds(args.seeds))
    heat = np.array([1.0 if node in seed_set else 0.0 for node in nodes])
    scores = expm(-args.time * laplacian).dot(heat)
    result = pd.DataFrame({"Gene_ID": nodes, "Diffusion_score": scores}).sort_values("Diffusion_score", ascending=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"saved heat-diffusion scores -> {args.output}")


if __name__ == "__main__":
    main()

