"""Calculate Morgan/Tanimoto similarities from two tab-separated name/SMILES files."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem


def read_smiles(path: Path) -> tuple[list[str], list]:
    table = pd.read_csv(path, sep="\t", header=None, names=["name", "smiles"])
    molecules, names = [], []
    for row in table.itertuples(index=False):
        molecule = Chem.MolFromSmiles(str(row.smiles).strip())
        if molecule is not None:
            molecules.append(molecule)
            names.append(str(row.name))
    return names, molecules


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-file", type=Path, required=True)
    parser.add_argument("--candidate-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--heatmap", type=Path)
    parser.add_argument("--radius", type=int, default=2)
    parser.add_argument("--n-bits", type=int, default=2048)
    args = parser.parse_args()

    template_names, templates = read_smiles(args.template_file)
    candidate_names, candidates = read_smiles(args.candidate_file)
    template_fp = [AllChem.GetMorganFingerprintAsBitVect(m, args.radius, nBits=args.n_bits) for m in templates]
    candidate_fp = [AllChem.GetMorganFingerprintAsBitVect(m, args.radius, nBits=args.n_bits) for m in candidates]
    matrix = np.array([[DataStructs.TanimotoSimilarity(a, b) for b in candidate_fp] for a in template_fp])
    result = pd.DataFrame(matrix, index=template_names, columns=candidate_names)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output)
    if args.heatmap:
        import matplotlib.pyplot as plt
        import seaborn as sns
        args.heatmap.parent.mkdir(parents=True, exist_ok=True)
        plt.figure(figsize=(10, 8))
        sns.heatmap(result, cmap="coolwarm", xticklabels=True, yticklabels=True)
        plt.tight_layout()
        plt.savefig(args.heatmap, dpi=300)
        plt.close()
    print(f"saved similarity matrix -> {args.output}")


if __name__ == "__main__":
    main()

