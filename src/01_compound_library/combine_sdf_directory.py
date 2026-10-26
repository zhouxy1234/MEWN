"""Combine individual SDF files in a directory into one SDF file."""

from __future__ import annotations

import argparse
from pathlib import Path
from rdkit import Chem


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    writer = Chem.SDWriter(str(args.output))
    count = 0
    for path in sorted(args.input_dir.glob("*.sdf")):
        for molecule in Chem.SDMolSupplier(str(path), removeHs=False):
            if molecule is not None:
                writer.write(molecule)
                count += 1
    writer.close()
    print(f"combined {count} molecules -> {args.output}")


if __name__ == "__main__":
    main()

