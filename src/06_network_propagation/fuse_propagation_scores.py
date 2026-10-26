"""Normalize and fuse PageRank, heat-diffusion and RWR scores."""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pagerank", type=Path, required=True)
    parser.add_argument("--diffusion", type=Path, required=True)
    parser.add_argument("--rwr", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    page = pd.read_csv(args.pagerank)
    diffusion = pd.read_csv(args.diffusion)
    rwr = pd.read_csv(args.rwr)
    merged = page.merge(diffusion, on="Gene_ID").merge(rwr, on="Gene_ID")
    score_columns = ["PageRank_score", "Diffusion_score", "RWR_score"]
    normalized = MinMaxScaler().fit_transform(merged[score_columns])
    merged[["PageRank_norm", "Diffusion_norm", "RWR_norm"]] = normalized
    merged["Fusion_score_avg"] = merged[["PageRank_norm", "Diffusion_norm", "RWR_norm"]].mean(axis=1)
    merged["Rank_PR"] = merged["PageRank_score"].rank(ascending=False)
    merged["Rank_Heat"] = merged["Diffusion_score"].rank(ascending=False)
    merged["Rank_RWR"] = merged["RWR_score"].rank(ascending=False)
    merged["Fusion_score_rankavg"] = merged[["Rank_PR", "Rank_Heat", "Rank_RWR"]].mean(axis=1).rank()
    result = merged.sort_values("Fusion_score_avg", ascending=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"saved fused scores -> {args.output}")


if __name__ == "__main__":
    main()

