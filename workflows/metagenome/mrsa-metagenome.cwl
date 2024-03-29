cwlVersion: v1.1
class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ResourceRequirement:
    ramMin: 2048
    coresMin: 1

inputs:
  sample_id: string
  fastq1: File
  fastq2: File
  kraken_db: Directory
  snippy_ref: File
outputs:
  krakenOutput:
    type: File
    outputSource: kraken2/kraken_output
  krakenReport:
    type: File
    outputSource: kraken2/kraken_report
  skesaContigs:
    type: File
    outputSource: skesa/contigs_out
  skesaGFA:
    type: File
    outputSource: gfa_connector/gfa_out
  snippyVCF:
    type: File
    outputSource: snippy/vcf_output
  snippyTxt:
    type: File
    outputSource: snippy/txt_output
  snippyAligned:
    type: File
    outputSource: snippy/aligned_fasta_output
  prokkaFAA:
    type: File
    outputSource: prokka/faa_output
  prokkaGFF:
    type: File
    outputSource: prokka/gff_output
  mlstTSV:
    type: File
    outputSource: mlst/tsv_output
  resistomeTSV:
    type: File
    outputSource: abricate_resfinder/tsv_output
  virulomeTSV:
    type: File
    outputSource: abricate_vfdb/tsv_output

steps:
  trimGalore:
    in:
      fastq1: fastq1
      fastq2: fastq2
    out: [fastq1_trimmed, fastq2_trimmed]
    run: trim_galore.cwl
  kraken2:
    in:
      database: kraken_db
      input_sequences: [trimGalore/fastq1_trimmed, trimGalore/fastq2_trimmed]
      report:
        default:
          output_report: "kraken_report.txt"
      paired:
        default: true
      gzip-compressed:
        default: true
    out: [kraken_output, kraken_report]
    run: kraken2.cwl
  skesa:
    in:
      reads: [trimGalore/fastq1_trimmed, trimGalore/fastq2_trimmed]
      contigs_out_name:
        default: "skesa_contigs.fa"
    out: [contigs_out]
    run: skesa.cwl
  gfa_connector:
    in:
      reads: [trimGalore/fastq1_trimmed, trimGalore/fastq2_trimmed]
      contigs: skesa/contigs_out
    out: [gfa_out]
    run: gfa_connector.cwl
  snippy:
    in:
      reference: snippy_ref
      R1: trimGalore/fastq1_trimmed
      R2: trimGalore/fastq2_trimmed
      outdir: sample_id
      force:
        default: true
    out: [vcf_output, aligned_fasta_output, txt_output]
    run: snippy.cwl
  prokka:
    in:
      fa_file: skesa/contigs_out
      force:
        default: true
      prefix: sample_id
    out: [faa_output, gff_output]
    run: prokka.cwl
  mlst:
    in:
      fa_file: skesa/contigs_out
    out: [tsv_output]
    run: mlst.cwl
  abricate_vfdb:
    in:
      fa_file: skesa/contigs_out
      db:
        default: "vfdb"
    out: [tsv_output]
    run: abricate.cwl
  abricate_resfinder:
    in:
      fa_file: skesa/contigs_out
      db:
        default: "resfinder"
    out: [tsv_output]
    run: abricate.cwl
