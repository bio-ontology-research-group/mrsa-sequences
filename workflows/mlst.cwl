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
    dockerPull: quay.io/biocontainers/mlst:2.19.0--0  

baseCommand: mlst
stdout: mlst.tsv

inputs:
  fa_file:
    type: File
    inputBinding:
      position: 1

outputs:
  tsv_output:
    type: stdout