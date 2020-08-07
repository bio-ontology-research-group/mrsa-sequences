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

arguments: ["ancestral"]

inputs:
  alignment:
    type: File
    inputBinding:
      position: 1
      prefix: '--alignment'
  tree:
    type: File
    inputBinding:
      position: 2
      prefix: '--tree'
  output:
    type: string?
    default: 'nt_muts.json'
    inputBinding:
      position: 2
      prefix: '--output-node-data'
  inference:
    type: string?
    default: 'joint'
    inputBinding:
      position: 2
      prefix: '--inference'

outputs:
  nt_muts:
    type: File
    outputBinding:
      glob: $(inputs.output)
