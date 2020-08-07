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

arguments: ["translate"]

inputs:
  tree:
    type: File
    inputBinding:
      position: 2
      prefix: '--tree'
  ancestral:
    type: File
    inputBinding:
      position: 1
      prefix: '--ancestral-sequence'
  reference:
    type: File
    inputBinding:
      position: 1
      prefix: '--reference-sequence'
  output:
    type: string?
    default: 'aa_muts.json'
    inputBinding:
      position: 2
      prefix: '--output'

outputs:
  aa_muts:
    type: File
    outputBinding:
      glob: $(inputs.output)
