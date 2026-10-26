"""Filter differential-expression tables into gene-signature lists."""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def genes(table: pd.DataFrame, log2fc: float, p_value: float) -> list[str]:
    required = {"Gene", "log2FC", "p_value"}
    if not required.issubset(table.columns):
        raise ValueError(f"Input must contain {sorted(required)}")
    selected = table[(table["log2FC"].abs() >= log2fc) & (table["p_value"] < p_value)]
    return selected["Gene"].astype(str).drop_duplicates().tolist()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--disease-vs-control", type=Path, required=True)
    parser.add_argument("--intervention-vs-disease", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--log2fc", type=float, default=1.5)
    parser.add_argument("--p-value", type=float, default=0.05)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    disease = genes(pd.read_csv(args.disease_vs_control), args.log2fc, args.p_value)
    intervention = genes(pd.read_csv(args.intervention_vs_disease), args.log2fc, args.p_value)
    (args.output_dir / "disease_signature.txt").write_text("\n".join(disease) + "\n", encoding="utf-8")
    (args.output_dir / "intervention_signature.txt").write_text("\n".join(intervention) + "\n", encoding="utf-8")
    print(f"disease genes: {len(disease)}; intervention genes: {len(intervention)}")


if __name__ == "__main__":
    main()

