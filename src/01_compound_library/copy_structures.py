"""Copy structure files listed in a text file into a standardized directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-list", type=Path, required=True)
    parser.add_argument("--source-folder", type=Path, required=True)
    parser.add_argument("--output-folder", type=Path, required=True)
    args = parser.parse_args()

    args.output_folder.mkdir(parents=True, exist_ok=True)
    requested = [line.strip() for line in args.file_list.read_text(encoding="utf-8").splitlines() if line.strip()]
    files_by_stem = {}
    for path in args.source_folder.rglob("*"):
        if path.is_file():
            files_by_stem.setdefault(path.stem.lower(), path)

    missing = []
    for name in requested:
        source = files_by_stem.get(Path(name).stem.lower())
        if source is None:
            missing.append(name)
            continue
        destination = args.output_folder / source.name
        shutil.copy2(source, destination)
        print(f"copied {source} -> {destination}")

    if missing:
        print("Missing files:")
        for name in missing:
            print(f"  {name}")


if __name__ == "__main__":
    main()

