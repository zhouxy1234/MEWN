"""Plot the distributions of the three propagation scores."""

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
    columns = ["PageRank_score", "Diffusion_score", "RWR_score"]
    long = table[columns].melt(var_name="Algorithm", value_name="Score")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 6))
    sns.violinplot(data=long, x="Algorithm", y="Score", inner="quartile")
    plt.yscale("log")
    plt.tight_layout()
    plt.savefig(args.output, dpi=300)
    plt.close()


if __name__ == "__main__":
    main()

