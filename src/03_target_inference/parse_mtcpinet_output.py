"""Filter MTCPINet/DTIModel predictions using an explicit score threshold."""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--score-column", default="Classification Score")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--sep", default=",")
    args = parser.parse_args()

    table = pd.read_csv(args.input, sep=args.sep)
    if args.score_column not in table.columns:
        raise ValueError(f"Missing score column {args.score_column!r}; columns: {list(table.columns)}")
    table[args.score_column] = pd.to_numeric(table[args.score_column], errors="coerce")
    result = table[table[args.score_column] >= args.threshold].copy()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"retained {len(result)} predictions -> {args.output}")


if __name__ == "__main__":
    main()

