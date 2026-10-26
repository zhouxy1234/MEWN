"""Calculate a cosine-similarity matrix from a gene-vector CSV file."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    table = pd.read_csv(args.input)
    if "Gene_ID" not in table.columns:
        raise ValueError("Input must contain a Gene_ID column")
    ids = table["Gene_ID"].astype(str).tolist()
    vectors = table.drop(columns=["Gene_ID"]).apply(pd.to_numeric, errors="raise").to_numpy()
    similarities = cosine_similarity(vectors, vectors)
    result = pd.DataFrame(similarities, index=ids, columns=ids)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output)
    print(f"saved {result.shape[0]} x {result.shape[1]} matrix -> {args.output}")


if __name__ == "__main__":
    main()

