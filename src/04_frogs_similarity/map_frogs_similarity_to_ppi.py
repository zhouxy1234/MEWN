"""Map FRoGS gene similarities to STRING PPI edges."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def read_table(path: Path) -> pd.DataFrame:
    return pd.read_excel(path) if path.suffix.lower() in {".xls", ".xlsx"} else pd.read_csv(path)


def lookup(matrix: pd.DataFrame, left: str, right: str, fallback: float) -> float:
    try:
        value = matrix.loc[left, right]
    except KeyError:
        try:
            value = matrix.loc[right, left]
        except KeyError:
            return fallback
    return fallback if pd.isna(value) or float(value) == 0 else float(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ppi", type=Path, required=True)
    parser.add_argument("--frogs-matrix", type=Path, required=True)
    parser.add_argument("--gene-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    ppi = read_table(args.ppi)
    matrix = pd.read_csv(args.frogs_matrix, index_col=0)
    matrix.index = matrix.index.astype(str)
    matrix.columns = matrix.columns.astype(str)
    mapping = read_table(args.gene_map)
    required = {"Protein1", "Protein2"}
    if not required.issubset(ppi.columns):
        raise ValueError(f"PPI table must contain {sorted(required)}")
    mapping["MyList"] = mapping["MyList"].astype(str).str.strip().str.upper()
    mapping["Gene ID"] = mapping["Gene ID"].astype(str)
    lookup_map = dict(zip(mapping["MyList"], mapping["Gene ID"]))
    ppi["Protein1"] = ppi["Protein1"].astype(str).str.strip().str.upper()
    ppi["Protein2"] = ppi["Protein2"].astype(str).str.strip().str.upper()
    ppi["Gene_ID_1"] = ppi["Protein1"].map(lookup_map)
    ppi["Gene_ID_2"] = ppi["Protein2"].map(lookup_map)
    values = matrix.to_numpy(dtype=float)
    non_diagonal = values[~np.eye(values.shape[0], dtype=bool)] if values.shape[0] > 1 else values.ravel()
    nonzero = non_diagonal[non_diagonal != 0]
    fallback = float(nonzero.mean()) if nonzero.size else 0.0
    ppi["frogs_similarity"] = [lookup(matrix, str(a), str(b), fallback) for a, b in zip(ppi["Gene_ID_1"], ppi["Gene_ID_2"])]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    ppi.to_csv(args.output, index=False)
    print(f"saved mapped PPI table -> {args.output}")


if __name__ == "__main__":
    main()

