"""Prepare a simple structure list for the external WHALES implementation."""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="Compound table with compound_id and sdf_path")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--id-column", default="compound_id")
    parser.add_argument("--structure-column", default="sdf_path")
    args = parser.parse_args()
    table = pd.read_csv(args.input)
    missing = [column for column in [args.id_column, args.structure_column] if column not in table.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    result = table[[args.id_column, args.structure_column]].rename(columns={args.id_column: "compound_id", args.structure_column: "structure_path"})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"prepared WHALES structure list -> {args.output}")


if __name__ == "__main__":
    main()

