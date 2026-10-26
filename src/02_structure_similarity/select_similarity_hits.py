"""Select per-template hits above a template-specific similarity percentile."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--percentile", type=float, default=0.95)
    args = parser.parse_args()

    matrix = pd.read_csv(args.input, index_col=0)
    records = []
    for template, row in matrix.iterrows():
        values = pd.to_numeric(row, errors="coerce").dropna()
        if values.empty:
            continue
        threshold = float(np.quantile(values.to_numpy(), args.percentile))
        for candidate, value in values.items():
            if float(value) > threshold:
                records.append({"template": template, "candidate": candidate, "similarity": float(value), "threshold": threshold})
    result = pd.DataFrame(records, columns=["template", "candidate", "similarity", "threshold"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"selected {len(result)} hits -> {args.output}")


if __name__ == "__main__":
    main()

