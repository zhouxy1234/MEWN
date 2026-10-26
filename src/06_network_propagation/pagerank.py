"""Run PageRank on a weighted PPI network."""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import networkx as nx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--alpha", type=float, default=0.85)
    args = parser.parse_args()
    table = pd.read_csv(args.input)
    required = ["Gene_ID_1", "Gene_ID_2", "final_weight"]
    missing = [column for column in required if column not in table.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    table[["Gene_ID_1", "Gene_ID_2"]] = table[["Gene_ID_1", "Gene_ID_2"]].astype(str)
    graph = nx.from_pandas_edgelist(table, "Gene_ID_1", "Gene_ID_2", edge_attr="final_weight")
    scores = nx.pagerank(graph, alpha=args.alpha, weight="final_weight")
    result = pd.DataFrame(scores.items(), columns=["Gene_ID", "PageRank_score"])
    result = result.sort_values("PageRank_score", ascending=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"saved PageRank scores -> {args.output}")


if __name__ == "__main__":
    main()

