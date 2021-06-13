#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: rgi main

inputs:
  fasta:
    type: File
    inputBinding:
      prefix: --input_sequence
  out_file:
    type: string?
    default: cards.out
    inputBinding:
      prefix: --output_file

outputs:
  rgi_out:
    type: File
    outputBinding:
      glob: $(inputs.out_file)

requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    coresMin: 8
    ramMin: 60720
  - class: DockerRequirement
    dockerPull: "finlaymaguire/rgi:latest"
