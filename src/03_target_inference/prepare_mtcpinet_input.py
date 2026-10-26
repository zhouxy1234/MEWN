"""Prepare a generic MTCPINet/DTIModel input table.

The exact column names required by a particular DTIModel release may differ.
Use this wrapper to standardize the local compound/protein identifiers, then
adapt the final export columns to the official repository's README.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compounds", type=Path, required=True, help="Table containing compound_id and smiles")
    parser.add_argument("--proteins", type=Path, required=True, help="Table containing protein_id and sequence")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compound-id", default="compound_id")
    parser.add_argument("--smiles", default="smiles")
    parser.add_argument("--protein-id", default="protein_id")
    parser.add_argument("--sequence", default="sequence")
    args = parser.parse_args()

    compounds = pd.read_csv(args.compounds)
    proteins = pd.read_csv(args.proteins)
    for table, columns, label in [
        (compounds, [args.compound_id, args.smiles], "compound"),
        (proteins, [args.protein_id, args.sequence], "protein"),
    ]:
        missing = [column for column in columns if column not in table.columns]
        if missing:
            raise ValueError(f"Missing {label} columns: {missing}")

    result = compounds[[args.compound_id, args.smiles]].copy()
    result = result.rename(columns={args.compound_id: "compound_id", args.smiles: "smiles"})
    result["key"] = 1
    proteins_small = proteins[[args.protein_id, args.sequence]].copy()
    proteins_small = proteins_small.rename(columns={args.protein_id: "protein_id", args.sequence: "sequence"})
    proteins_small["key"] = 1
    result = result.merge(proteins_small, on="key").drop(columns="key")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"prepared {len(result)} compound-protein pairs -> {args.output}")


if __name__ == "__main__":
    main()

