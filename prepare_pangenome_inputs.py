import json
import argparse
import os
import shutil
from pathlib import Path

def validate_inputs(args):
    """Perform all pre-flight checks before generating the input file."""
    print("--- Running Pre-flight Validations ---")
    all_ok = True

    # 1. Check for cwl-runner
    if not shutil.which("cwl-runner"):
        print("❌ Error: `cwl-runner` not found in your PATH.")
        print("   Please install it (e.g., `pip install cwl-runner`) and ensure it is accessible.")
        all_ok = False
    else:
        print("✅ `cwl-runner` is installed.")

    # 2. Check that workflow file exists
    workflow_file = Path("workflows/pangenome/mrsa-pangenome.cwl")
    if not workflow_file.is_file():
        print(f"❌ Error: Main workflow file not found at '{workflow_file}'")
        all_ok = False
    else:
        print(f"✅ Main workflow file found.")


    # 3. Check main input paths
    samples_dir = Path(args.samples_dir)
    if not samples_dir.is_dir():
        print(f"❌ Error: Samples directory not found at '{samples_dir}'")
        all_ok = False
    else:
        print("✅ Samples directory found.")

    reference_fasta = Path(args.reference_fasta)
    if not reference_fasta.is_file():
        print(f"❌ Error: Reference FASTA file not found at '{reference_fasta}'")
        all_ok = False
    else:
        print("✅ Reference FASTA found.")

    reference_genbank = Path(args.reference_genbank)
    if not reference_genbank.is_file():
        print(f"❌ Error: Reference GenBank file not found at '{reference_genbank}'")
        all_ok = False
    else:
        print("✅ Reference GenBank found.")

    metadata_file = Path(args.metadata)
    if not metadata_file.is_file():
        print(f"❌ Error: Metadata file not found at '{metadata_file}'")
        all_ok = False
    else:
        print("✅ Metadata file found.")

    print("-" * 38)
    return all_ok

def prepare_pangenome_inputs(args):
    """
    Scans a directory for sample data and generates a JSON input file
    for the mrsa-pangenome.cwl workflow.
    """
    if not validate_inputs(args):
        print("\nValidation failed. Please fix the errors above before proceeding.")
        return

    samples_dir = Path(args.samples_dir)
    gff_files = []
    sample_dirs = []
    snippy_prefix = args.snippy_prefix

    print("\n--- Scanning for Sample Data ---")
    for sample_path in sorted(samples_dir.iterdir()):
        if sample_path.is_dir():
            # Check for required files within each sample directory
            found_gff = list(sample_path.glob("*.gff"))
            snippy_fasta = sample_path / f"{snippy_prefix}.aligned.fa"
            snippy_vcf = sample_path / f"{snippy_prefix}.vcf"

            if found_gff and snippy_fasta.is_file() and snippy_vcf.is_file():
                print(f"  + Found valid sample '{sample_path.name}'")
                gff_files.append({"class": "File", "path": str(found_gff[0].resolve())})
                sample_dirs.append({"class": "Directory", "path": str(sample_path.resolve())})
            else:
                print(f"  - Warning: Skipping directory '{sample_path.name}'. Missing required files.")
                if not found_gff:
                    print("    - Missing .gff file")
                if not snippy_fasta.is_file():
                    print(f"    - Missing {snippy_fasta.name}")
                if not snippy_vcf.is_file():
                    print(f"    - Missing {snippy_vcf.name}")


    if not gff_files:
        print("\nError: No valid sample directories found. Cannot generate input file.")
        return

    # --- Construct the JSON object ---
    pangenome_inputs = {
        "gff_files": gff_files,
        "reference": {
            "class": "File",
            "path": str(Path(args.reference_fasta).resolve())
        },
        "reference_gb": {
            "class": "File",
            "path": str(Path(args.reference_genbank).resolve())
        },
        "dirs": sample_dirs,
        "metadata": {
            "class": "File",
            "path": str(Path(args.metadata).resolve())
        },
        "snippy_inprefix": snippy_prefix
    }

    # --- Write the output JSON file ---
    output_json = Path(args.output_json)
    with open(output_json, 'w') as f:
        json.dump(pangenome_inputs, f, indent=4)

    print(f"\nSuccessfully created workflow input file at '{output_json}'")
    print("\nTo run the pangenome workflow, use the following command:")
    print("-" * 70)
    print(f"cwl-runner {Path('workflows/pangenome/mrsa-pangenome.cwl').resolve()} {output_json.resolve()}")
    print("-" * 70)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Prepare and validate an input JSON file for the mrsa-pangenome.cwl workflow."
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
        help="Prefix for the snippy output files used in validation. (Default: snps)"
    )

    args = parser.parse_args()
    prepare_pangenome_inputs(args)