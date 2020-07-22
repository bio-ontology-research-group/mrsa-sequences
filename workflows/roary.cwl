#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

requirements:
  ResourceRequirement:
    ramMin: 8000
    coresMin: 1
  InlineJavascriptRequirement: {}
  ScatterFeatureRequirement: {}
  DockerRequirement:
    dockerPull: quay.io/biocontainers/roary:3.13.0--pl526h516909a_0

baseCommand: roary

inputs:
  gff_files:
    type: File[]
    inputBinding:
      position: 1
  outdir:
    type: string?
    default: 'roary'
    inputBinding:
      position: 1
      prefix: '-f'
  alignment:
    type: boolean?
    default: true
    inputBinding:
      position: 1
      prefix: '-e'
  fast:
    type: boolean?
    default: true
    inputBinding:
      position: 1
      prefix: '-n'
  verbose:
    type: boolean?
    inputBinding:
      position: 1
      prefix: '-v'

outputs:
  statistics:
    type: File
    outputBinding:
      glob: $(inputs.outdir)/summary_statistics.txt
  gene_presence_absence:
    type: File
    outputBinding:
      glob: $(inputs.outdir)/gene_presence_absence.csv
  pangenome:
    type: File
    outputBinding:
      glob: $(inputs.outdir)/pan_genome_reference.fa