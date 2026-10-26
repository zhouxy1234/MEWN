"""Merge structure-transferred and MTCPINet-predicted compound-target pairs."""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def read_table(path: Path) -> pd.DataFrame:
    return pd.read_excel(path) if path.suffix.lower() in {".xls", ".xlsx"} else pd.read_csv(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure-pairs", type=Path, required=True)
    parser.add_argument("--mtcpinet-pairs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compound-column", default="compound")
    parser.add_argument("--target-column", default="target")
    args = parser.parse_args()

    structural = read_table(args.structure_pairs).copy()
    predicted = read_table(args.mtcpinet_pairs).copy()
    required = [args.compound_column, args.target_column]
    for name, table in [("structure", structural), ("MTCPINet", predicted)]:
        missing = [column for column in required if column not in table.columns]
        if missing:
            raise ValueError(f"{name} table is missing columns: {missing}")
    structural["evidence_source"] = "structure_similarity"
    predicted["evidence_source"] = "MTCPINet"
    result = pd.concat([structural, predicted], ignore_index=True)
    result = result.drop_duplicates(subset=required, keep="first")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"saved {len(result)} integrated pairs -> {args.output}")


if __name__ == "__main__":
    main()

