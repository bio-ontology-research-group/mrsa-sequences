cwlVersion: v1.1
class: Workflow
requirements:
  MultipleInputFeatureRequirement: {}
inputs:
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
  snippyVCF:
    type: File
    outputSource: snippy/vcf_output

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
      fastq: [trimGalore/fastq1_trimmed, trimGalore/fastq2_trimmed]
      contigs_out_name:
        default: "skesa_contigs.fa"
    out: [contigs_out]
    run: skesa.cwl
  snippy:
    in:
      reference: snippy_ref
      contigs: skesa/contigs_out
      force:
        default: true
    out: [vcf_output]
    run: snippy.cwl

$namespaces:
  edam: http://edamontology.org/
  s: http://schema.org/
