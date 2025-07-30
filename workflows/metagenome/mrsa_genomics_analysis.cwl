cwlVersion: v1.1
class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  StepInputExpressionRequirement: {}
  ResourceRequirement:
    ramMin: 4096
    coresMin: 2

inputs:
  # Inputs for the entire workflow
  sample_id: string
  fastq1: File
  fastq2: File

  # Database inputs
  kraken_db: Directory
  snippy_ref: File

outputs:
  # QC Outputs
  trimming_report_r1:
    type: File
    outputSource: trim_galore/trimming_report_r1
  trimming_report_r2:
    type: File
    outputSource: trim_galore/trimming_report_r2

  # Classification Outputs
  kraken_report:
    type: File
    outputSource: kraken2/kraken_report
  kraken_output:
    type: File
    outputSource: kraken2/kraken_output

  # Assembly Output
  assembly_contigs:
    type: File
    outputSource: skesa/contigs_out

  # Annotation Outputs
  prokka_gff:
    type: File
    outputSource: prokka/gff_output
  prokka_faa:
    type: File
    outputSource: prokka/faa_output
  prokka_fna:
    type: File
    outputSource: prokka/fna_output

  # AMR & Resistance Outputs
  rgi_results:
    type: File
    outputSource: rgi/results
  abricate_resfinder_results:
    type: File
    outputSource: abricate_resfinder/tsv_output

  # Typing and Variant Outputs
  mlst_results:
    type: File
    outputSource: mlst/tsv_output
  snippy_variants:
    type: File
    outputSource: snippy/vcf_output
  snippy_report:
    type: File
    outputSource: snippy/txt_output

steps:
  # 1. Quality Control and Trimming
  trim_galore:
    run: trim_galore.cwl
    in:
      fastq1: fastq1
      fastq2: fastq2
    out: [fastq1_trimmed, fastq2_trimmed, trimming_report_r1, trimming_report_r2]

  # 2. Taxonomic Classification (runs in parallel with assembly)
  kraken2:
    run: kraken2.cwl
    in:
      database: kraken_db
      input_sequences: [trim_galore/fastq1_trimmed, trim_galore/fastq2_trimmed]
      paired:
        default: true
      gzip-compressed:
        default: true
    out: [kraken_output, kraken_report]

  # 3. De Novo Assembly
  skesa:
    run: skesa.cwl
    in:
      reads: [trim_galore/fastq1_trimmed, trim_galore/fastq2_trimmed]
    out: [contigs_out]

  # 4. Gene Annotation (depends on assembly)
  prokka:
    run: prokka.cwl
    in:
      fa_file: skesa/contigs_out
      prefix: sample_id
      force:
        default: true
    out: [gff_output, faa_output, fna_output]

  # 5. AMR Gene Detection (depends on assembly)
  rgi:
    run: rgi.cwl
    in:
      input_file: skesa/contigs_out
    out: [results]

  abricate_resfinder:
    run: abricate.cwl
    in:
      fa_file: skesa/contigs_out
      db:
        default: "resfinder"
    out: [tsv_output]

  # 6. Sequence Typing (depends on assembly)
  mlst:
    run: mlst.cwl
    in:
      fa_file: skesa/contigs_out
    out: [tsv_output]

  # 7. Variant Calling (runs in parallel with assembly)
  snippy:
    run: snippy.cwl
    in:
      reference: snippy_ref
      R1: trim_galore/fastq1_trimmed
      R2: trim_galore/fastq2_trimmed
      outdir: sample_id
      force:
        default: true
    out: [vcf_output, txt_output]