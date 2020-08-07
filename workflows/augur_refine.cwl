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

arguments: ["refine"]

inputs:
  alignment:
    type: File
    inputBinding:
      position: 1
      prefix: '--alignment'
  tree_raw:
    type: File
    inputBinding:
      position: 2
      prefix: '--tree'
  metadata:
    type: File
    inputBinding:
      position: 2
      prefix: '--metadata'
  output_tree:
    type: string?
    default: 'tree.nwk'
    inputBinding:
      position: 2
      prefix: '--output-tree'
  output_node_data:
    type: string?
    default: 'branch_lengths.json'
    inputBinding:
      position: 2
      prefix: '--output-node-data'
  timetree:
    type: boolean?
    default: true
    inputBinding:
      position: 2
      prefix: '--timetree'
  coalescent:
    type: string?
    default: 'opt'
    inputBinding:
      position: 2
      prefix: '--coalescent'
  date_confidence:
    type: boolean?
    default: true
    inputBinding:
      position: 2
      prefix: --date-confidence
  date_inference:
    type: string?
    default: 'marginal'
    inputBinding:
      position: 2
      prefix: --date-inference
  clock_filter_iqd:
    type: int?
    default: 4
    inputBinding:
      position: 2
      prefix: --clock-filter-iqd

outputs:
  out_tree:
    type: File
    outputBinding:
      glob: $(inputs.output_tree)
  out_node_data:
    type: File
    outputBinding:
      glob: $(inputs.output_node_data)
