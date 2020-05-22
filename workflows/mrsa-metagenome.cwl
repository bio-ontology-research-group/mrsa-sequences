cwlVersion: v1.1
class: Workflow
requirements:
  MultipleInputFeatureRequirement: {}
inputs:
  fastq1: File
  fastq2: File
  kraken_db: Directory
outputs:
  krakenReport:
    type: File
    outputSource: kraken2/kraken_report

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

$namespaces:
  edam: http://edamontology.org/
  s: http://schema.org/
