

import json
import argparse
import os
from pathlib import Path

def prepare_pangenome_inputs(args):
    """
    Scans a directory for sample data and generates a JSON input file
    for the mrsa-pangenome.cwl workflow.
    """
    samples_dir = Path(args.samples_dir)
    reference_fasta = Path(args.reference_fasta)
    reference_genbank = Path(args.reference_genbank)
    metadata_file = Path(args.metadata)
    output_json = Path(args.output_json)

    # --- Validation ---
    if not samples_dir.is_dir():
        print(f"Error: Samples directory not found at '{samples_dir}'")
        return

    if not reference_fasta.is_file():
        print(f"Error: Reference FASTA file not found at '{reference_fasta}'")
        return

    if not reference_genbank.is_file():
        print(f"Error: Reference GenBank file not found at '{reference_genbank}'")
        return

    if not metadata_file.is_file():
        print(f"Error: Metadata file not found at '{metadata_file}'")
        return

    # --- Find sample directories and GFF files ---
    gff_files = []
    sample_dirs = []

    print(f"Scanning for samples in '{samples_dir}'...")
    for sample_path in sorted(samples_dir.iterdir()):
        if sample_path.is_dir():
            found_gff = list(sample_path.glob("*.gff"))
            if found_gff:
                print(f"  + Found sample '{sample_path.name}' with GFF file '{found_gff[0].name}'")
                gff_files.append({"class": "File", "path": str(found_gff[0].resolve())})
                sample_dirs.append({"class": "Directory", "path": str(sample_path.resolve())})
            else:
                print(f"  - Warning: No .gff file found in directory '{sample_path.name}'. Skipping.")

    if not gff_files:
        print("Error: No GFF files found. Cannot generate input file.")
        return

    # --- Construct the JSON object ---
    pangenome_inputs = {
        "gff_files": gff_files,
        "reference": {
            "class": "File",
            "path": str(reference_fasta.resolve())
        },
        "reference_gb": {
            "class": "File",
            "path": str(reference_genbank.resolve())
        },
        "dirs": sample_dirs,
        "metadata": {
            "class": "File",
            "path": str(metadata_file.resolve())
        },
        "snippy_inprefix": args.snippy_prefix
    }

    # --- Write the output JSON file ---
    with open(output_json, 'w') as f:
        json.dump(pangenome_inputs, f, indent=4)

    print(f"\nSuccessfully created workflow input file at '{output_json}'")
    print("\nTo run the pangenome workflow, use the following command:")
    print("-" * 70)
    print(f"cwl-runner workflows/pangenome/mrsa-pangenome.cwl {output_json}")
    print("-" * 70)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Prepare an input JSON file for the mrsa-pangenome.cwl workflow."
    )
    parser.add_argument(
        "--samples-dir",
        required=True,
        help="Directory containing subdirectories for each sample."
    )
    parser.add_argument(
        "--reference-fasta",
        required=True,
        help="Path to the reference genome in FASTA format."
    )
    parser.add_argument(
        "--reference-genbank",
        required=True,
        help="Path to the reference genome in GenBank format."
    )
    parser.add_argument(
        "--metadata",
        required=True,
        help="Path to the metadata file (e.g., metadata.tsv)."
    )
    parser.add_argument(
        "--output-json",
        default="pangenome-inputs.json",
        help="Name for the output JSON file. (Default: pangenome-inputs.json)"
    )
    parser.add_argument(
        "--snippy-prefix",
        default="snps",
        help="Prefix for the snippy output files. (Default: snps)"
    )

    args = parser.parse_args()
    prepare_pangenome_inputs(args)

