"""Calculate a Morgan/Tanimoto similarity matrix from two SDF files."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem


def load_sdf(path: Path):
    supplier = Chem.SDMolSupplier(str(path), removeHs=False)
    molecules = [mol for mol in supplier if mol is not None]
    names = [mol.GetProp("_Name") if mol.HasProp("_Name") else f"ID_{i}" for i, mol in enumerate(molecules)]
    return molecules, names


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-sdf", type=Path, required=True)
    parser.add_argument("--candidate-sdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--radius", type=int, default=2)
    parser.add_argument("--n-bits", type=int, default=2048)
    args = parser.parse_args()

    templates, template_names = load_sdf(args.template_sdf)
    candidates, candidate_names = load_sdf(args.candidate_sdf)
    template_fp = [AllChem.GetMorganFingerprintAsBitVect(m, args.radius, nBits=args.n_bits) for m in templates]
    candidate_fp = [AllChem.GetMorganFingerprintAsBitVect(m, args.radius, nBits=args.n_bits) for m in candidates]
    matrix = np.array([[DataStructs.TanimotoSimilarity(a, b) for b in candidate_fp] for a in template_fp])
    result = pd.DataFrame(matrix, index=template_names, columns=candidate_names)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output)
    print(f"saved {result.shape[0]} x {result.shape[1]} matrix -> {args.output}")


if __name__ == "__main__":
    main()

