#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: gfa_connector

inputs:
  reads:
    type:
      - File?
      - File[]?
    inputBinding:
      prefix: --reads
      itemSeparator: ","
  use_paired_ends:
    type: boolean?
    inputBinding:
      prefix: --use_paired_ends
  contigs:
    type: File?
    inputBinding:
      prefix: --contigs
  gfa:
    type: string?
    default: skesa.gfa
    inputBinding:
      prefix: --gfa
  csv:
    type: string?
    default: skesa.csv
    inputBinding:
      prefix: --csv
  cores:
    type: int?
    default: 0
    inputBinding:
      prefix: --cores

outputs:
  gfa_out:
    type: File
    outputBinding:
      glob: $(inputs.gfa)
  csv_out:
    type: File
    outputBinding:
      glob: $(inputs.csv)

requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    coresMin: 8
    ramMin: 30720
  - class: DockerRequirement
    dockerPull: "staphb/skesa:2.4.0"
