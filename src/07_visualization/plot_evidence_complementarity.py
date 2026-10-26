"""Plot normalized STRING and FRoGS evidence."""

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
    required = ["norm_string", "norm_frogs"]
    if any(column not in table.columns for column in required):
        raise ValueError(f"Input must contain {required}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 7))
    sns.scatterplot(data=table, x="norm_string", y="norm_frogs", alpha=0.5, s=15)
    plt.axhline(table["norm_frogs"].mean(), color="red", linestyle=":")
    plt.axvline(table["norm_string"].mean(), color="blue", linestyle=":")
    plt.xlabel("Normalized STRING score")
    plt.ylabel("Normalized FRoGS similarity")
    plt.tight_layout()
    plt.savefig(args.output, dpi=300)
    plt.close()


if __name__ == "__main__":
    main()

