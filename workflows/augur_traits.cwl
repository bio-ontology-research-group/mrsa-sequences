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

arguments: ["traits"]

inputs:
  tree:
    type: File
    inputBinding:
      position: 1
      prefix: '--tree'
  metadata:
    type: File
    inputBinding:
      position: 2
      prefix: '--metadata'
  output:
    type: string?
    default: 'traits.json'
    inputBinding:
      position: 3
      prefix: '--output'
  columns:
    type: string[]?
    default: ['region', 'country']
    inputBinding:
      position: 4
      prefix: '--columns'
  confidence:
    type: boolean?
    inputBinding:
      position: 5
      prefix: '--confidence'

outputs:
  traits:
    type: File
    outputBinding:
      glob: $(inputs.output)
