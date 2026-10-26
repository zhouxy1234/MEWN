"""Match compound names in a text file to the first column of an Excel table."""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compound-list", type=Path, required=True)
    parser.add_argument("--target-table", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    names = {line.strip() for line in args.compound_list.read_text(encoding="utf-8").splitlines() if line.strip()}
    table = pd.read_excel(args.target_table)
    first_column = table.columns[0]
    result = table[table[first_column].astype(str).str.strip().isin(names)].copy()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_excel(args.output, index=False)
    print(f"matched {len(result)} rows -> {args.output}")


if __name__ == "__main__":
    main()

