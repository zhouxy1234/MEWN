"""Summarize evidence correlation, conflict rate and DAFP parameters."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tau", type=float, default=0.5)
    args = parser.parse_args()
    table = pd.read_csv(args.input)
    string = pd.to_numeric(table["norm_string"], errors="coerce")
    frogs = pd.to_numeric(table["norm_frogs"], errors="coerce")
    valid = string.notna() & frogs.notna()
    rho, p_value = spearmanr(string[valid], frogs[valid])
    conflict_rate = float((np.abs(string[valid] - frogs[valid]) > args.tau).mean() * 100)
    summary = "\n".join([
        "=== Evidence relationship ===",
        f"Spearman(s,f): rho={rho:.6f}, p={p_value:.3e}",
        f"Conflict rate (|s-f| > tau={args.tau}): {conflict_rate:.2f}%",
    ])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(summary + "\n", encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()

