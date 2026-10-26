"""Plot Spearman rank correlations among propagation algorithms."""

from __future__ import annotations

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    table = pd.read_csv(args.input)
    score_columns = ["PageRank_score", "Diffusion_score", "RWR_score"]
    ranks = table[score_columns].rank(ascending=False)
    correlation = ranks.corr(method="spearman")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 6))
    sns.heatmap(correlation, cmap="coolwarm", vmin=-1, vmax=1, linewidths=0.5, linecolor="black")
    plt.title("Spearman rank correlation")
    plt.tight_layout()
    plt.savefig(args.output, dpi=300)
    plt.close()
    print(correlation)


if __name__ == "__main__":
    main()

