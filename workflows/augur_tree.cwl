#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

requirements:
  ResourceRequirement:
    ramMin: 8000
    coresMin: 2
  InlineJavascriptRequirement: {}
  ScatterFeatureRequirement: {}
  DockerRequirement:
    dockerPull: quay.io/biocontainers/augur:7.0.2--py_0

baseCommand: augur

arguments: ["tree"]

inputs:
  fasta:
    type: File?
    inputBinding:
      position: 1
      prefix: '--alignment'
  output:
    type: string?
    default: 'tree_raw.nwk'
    inputBinding:
      position: 2
      prefix: '--output'

outputs:
  tree_out:
    type: File
    outputBinding:
      glob: $(inputs.output)
