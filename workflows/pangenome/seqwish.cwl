#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  DockerRequirement:
    dockerPull: "quay.io/biocontainers/seqwish:0.4.1--h2e03b76_1"
  ResourceRequirement:
    coresMin: 16
    ramMin: 250000

baseCommand: seqwish

inputs:
  readsFA:
    type: File
    inputBinding:
      position: 1
      prefix: "-s"
  readsPAF:
    type: File
    inputBinding:
      position: 2
      prefix: "-p"
  gfa_name:
    type: string?
    default: seqwish.gfa
    inputBinding:
      position: 3
      prefix: "-g"

outputs:
  seqwishGFA:
    type: File
    outputBinding:
      glob: $(inputs.gfa_name)
