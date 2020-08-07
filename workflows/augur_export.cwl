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

arguments: ["export", "v2"]

inputs:
  tree:
    type: File
    inputBinding:
      position: 2
      prefix: '--tree'
  metadata:
    type: File
    inputBinding:
      position: 2
      prefix: '--metadata'
  node_data:
    type: File[]
    inputBinding:
      position: 2
      prefix: '--node-data'
  colors:
    type: File?
    inputBinding:
      position: 2
      prefix: '--colors'
  lat_longs:
    type: File?
    inputBinding:
      position: 2
      prefix: '--lat-longs'
  auspice_config:
    type: File?
    inputBinding:
      position: 2
      prefix: '--auspice-config'
  output:
    type: string?
    default: 'output.json'
    inputBinding:
      position: 2
      prefix: '--output'

outputs:
  out_file:
    type: File
    outputBinding:
      glob: $(inputs.output)
