"""Retrieve PubChem SMILES and generate RDKit 3D SDF files."""

from __future__ import annotations

import argparse
from pathlib import Path

import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import AllChem


def make_structure(cid: str, output: Path) -> None:
    compound = pcp.Compound.from_cid(cid)
    smiles = compound.isomeric_smiles
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise ValueError(f"Invalid SMILES for CID {cid}: {smiles}")
    molecule = Chem.AddHs(molecule)
    if AllChem.EmbedMolecule(molecule, randomSeed=0xF00D) != 0:
        raise ValueError(f"Could not embed CID {cid}")
    AllChem.UFFOptimizeMolecule(molecule)
    molecule.SetProp("_Name", str(cid))
    writer = Chem.SDWriter(str(output))
    writer.write(molecule)
    writer.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cid-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    cids = [line.strip() for line in args.cid_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    for cid in cids:
        output = args.output_dir / f"{cid}.sdf"
        if output.exists() and not args.overwrite:
            print(f"skip existing {output}")
            continue
        try:
            make_structure(cid, output)
            print(f"created {output}")
        except Exception as exc:  # continue so one failed CID does not stop the batch
            print(f"failed CID {cid}: {exc}")


if __name__ == "__main__":
    main()

