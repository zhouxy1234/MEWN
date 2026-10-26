"""Plot a similarity matrix stored as a CSV file."""

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
    parser.add_argument("--vmax", type=float, default=None)
    args = parser.parse_args()
    matrix = pd.read_csv(args.input, index_col=0).apply(pd.to_numeric, errors="coerce").fillna(0)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(16, 9))
    sns.heatmap(matrix, cmap="viridis", vmin=0, vmax=args.vmax, annot=False)
    plt.xlabel("Candidate compounds")
    plt.ylabel("Template compounds")
    plt.tight_layout()
    plt.savefig(args.output, dpi=300)
    plt.close()
    print(f"saved figure -> {args.output}")


if __name__ == "__main__":
    main()

