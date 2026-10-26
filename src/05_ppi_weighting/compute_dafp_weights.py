"""Calculate study-specific DAFP weights for PPI edges."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def read_table(path: Path) -> pd.DataFrame:
    return pd.read_excel(path) if path.suffix.lower() in {".xls", ".xlsx"} else pd.read_csv(path)


def minmax(values: pd.Series) -> np.ndarray:
    array = pd.to_numeric(values, errors="coerce").fillna(0).to_numpy(dtype=float).reshape(-1, 1)
    return MinMaxScaler().fit_transform(array).ravel()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gamma", type=float, default=1.0)
    parser.add_argument("--lambda", dest="lam", type=float, default=0.1)
    parser.add_argument("--epsilon", type=float, default=1.0e-8)
    args = parser.parse_args()

    table = read_table(args.input)
    required = ["Gene_ID_1", "Gene_ID_2", "stringdb::score", "frogs_similarity"]
    missing = [column for column in required if column not in table.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    string_score = minmax(table["stringdb::score"])
    frogs_score = minmax(table["frogs_similarity"])
    alpha = string_score / (string_score + frogs_score + args.epsilon)
    delta = 1.0 + args.lam * np.abs(string_score - frogs_score) ** args.gamma
    weight = (alpha * string_score + (1.0 - alpha) * frogs_score) / (delta + args.epsilon)
    table["norm_string"] = string_score
    table["norm_frogs"] = frogs_score
    table["alpha_ij"] = alpha
    table["delta_ij"] = delta
    table["final_weight"] = np.clip(weight, 0.0, 1.0)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output, index=False)
    print(f"saved weighted PPI ({len(table)} edges) -> {args.output}")


if __name__ == "__main__":
    main()

