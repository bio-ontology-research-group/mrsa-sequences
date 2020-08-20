#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    coresMin: 8
    ramMin: 16000
  - class: DockerRequirement
    dockerPull: "coolmaksat/deepgoplus"

baseCommand: deepgoplus

inputs:
  fasta:
    type: File
    inputBinding:
      prefix: --input-file
  data_root:
    type: Directory
    inputBinding:
      prefix: --data-root
  out_file:
    type: string?
    default: results.tsv
    inputBinding:
      prefix: --out-file

outputs:
  output:
    type: File
    outputBinding:
      glob: $(inputs.out_file)

