# MRSA Sequence Analysis Workflows

This repository contains a suite of tools and workflows for the analysis of Methicillin-resistant Staphylococcus aureus (MRSA) sequences. It provides reproducible, command-line-driven analysis pipelines using the Common Workflow Language (CWL).

The repository was originally designed for use with the Arvados platform but can be run locally on any system with a CWL runner (e.g., `cwl-runner` or `toil`).

## Installation

To get started, you will need to set up a Python environment and install the required dependencies.

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/bio-ontology-research-group/mrsa-sequences.git
    cd mrsa-sequences
    ```

2.  **System Dependencies:** Ensure you have Python and the necessary development libraries installed. On Debian/Ubuntu, you can run:
    ```sh
    sudo apt-get update
    sudo apt-get install -y virtualenv git libcurl4-openssl-dev build-essential python3-dev libssl-dev libxml2-dev libxslt1-dev
    ```

3.  **Create a Python virtual environment:**
    ```sh
    virtualenv --python python3 venv
    source venv/bin/activate
    ```
    *Note: You will need to run `source venv/bin/activate` each time you work in a new terminal session.*

4.  **Install Python packages:**
    ```sh
    pip install -r requirements.txt
    ```

## Available Workflows

This repository includes two primary analysis workflows located in the `workflows/` directory.

### 1. Genomics Analysis Pipeline (`mrsa_genomics_analysis.cwl`)

This workflow performs a comprehensive analysis of a single MRSA isolate from raw, paired-end FASTQ reads.

**Pipeline Steps:**

1.  **QC & Trimming (`trim_galore`)**: Cleans raw reads by removing low-quality bases and adapter sequences.
2.  **Taxonomic Classification (`kraken2`)**: Identifies the species present in the sample.
3.  ***De Novo* Assembly (`skesa`)**: Assembles the cleaned reads into a draft genome.
4.  **Gene Annotation (`prokka`)**: Annotates the assembled genome to identify genes.
5.  **AMR Gene Detection (`rgi`, `abricate`)**: Scans the assembly for known antimicrobial resistance genes.
6.  **Sequence Typing (`mlst`)**: Determines the Multi-Locus Sequence Type (MLST) of the isolate.
7.  **Variant Calling (`snippy`)**: Compares the reads to a reference genome to identify SNPs and other variants.

### 2. Pangenome Analysis Pipeline (`mrsa-pangenome.cwl`)

This workflow analyzes a collection of MRSA genomes to understand their evolutionary relationships and shared gene content.

**Pipeline Steps:**

1.  **Core SNP Analysis (`snippy-core`)**: Identifies core genome SNPs from multiple genome assemblies.
2.  **Phylogenetic Tree Construction (`iqTree`)**: Builds a maximum-likelihood phylogenetic tree from the core genome alignment.
3.  **Pangenome Characterization (`roary`)**: Identifies the core and accessory genes across all input genomes.
4.  **Visualization (`roary2svg`)**: Generates an SVG image of the pangenome.

## Usage

### Running the Genomics Analysis Pipeline

1.  **Edit the input file:** Open `workflows/metagenome/mrsa_genomics_analysis.json` and replace the placeholder paths with the absolute paths to your data (FASTQ files, Kraken2 database, and reference FASTA).

2.  **Execute the workflow:**
    ```sh
    cwl-runner workflows/metagenome/mrsa_genomics_analysis.cwl workflows/metagenome/mrsa_genomics_analysis.json
    ```

### Running the Pangenome Analysis Pipeline

1.  **Prepare your data:** Ensure you have a directory containing a subdirectory for each of your samples. Each sample subdirectory must contain a GFF file (from a tool like Prokka) and the output from `snippy`.

2.  **Generate the input file:** Use the included `prepare_pangenome_inputs.py` script to automatically create the JSON input file for the workflow.
    ```sh
    python prepare_pangenome_inputs.py \
        --samples-dir /path/to/your/samples \
        --reference-fasta /path/to/your/reference.fasta \
        --reference-genbank /path/to/your/reference.gb \
        --metadata /path/to/your/metadata.tsv \
        --output-json pangenome-inputs.json
    ```

3.  **Execute the workflow:**
    ```sh
    cwl-runner workflows/pangenome/mrsa-pangenome.cwl pangenome-inputs.json
    ```