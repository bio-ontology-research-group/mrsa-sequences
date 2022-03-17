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
  snippy_ref: File
outputs:
  snippyVCF:
    type: File
    outputSource: snippy/vcf_output
  snippyOutdir:
    type: Directory
    outputSource: snippy/out_directory

steps:
  snippy:
    in:
      reference: snippy_ref
      R1: fastq1
      R2: fastq2
      outdir: sample_id
      force:
        default: true
    out: [vcf_output, out_directory]
    run: snippy.cwl
