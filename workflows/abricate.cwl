#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

requirements:
  ResourceRequirement:
    ramMin: 8000
    coresMin: 1
    coresMax: 2
  InlineJavascriptRequirement: {}
  ScatterFeatureRequirement: {}
  DockerRequirement:
    dockerPull: quay.io/biocontainers/abricate:1.0.1--h1341992_0

baseCommand: abricate
stdout: abricate_$(inputs.db).tsv

inputs:
  fa_file:
    type: File
    inputBinding:
      position: 1
  db:
    type: string?
    default: 'resfinder'
    inputBinding:
      position: 1
      prefix: '--db'

outputs:
  tsv_output:
    type: stdout