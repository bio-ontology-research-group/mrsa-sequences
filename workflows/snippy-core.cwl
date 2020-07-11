#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.0

baseCommand: snippy-core

inputs:
  reference:
    type: File
    inputBinding:
      position: 2
      prefix: '--ref'
    label: 'Reference genome. Supports FASTA, GenBank, EMBL (not GFF) (default '''')'
  dirs:
    type: Directory[]
    inputBinding:
      position: 2
    label: 'Output dirs from snippy'

outputs:
  alignments:
    type: File
    outputBinding:
      glob: core.full.aln
  outputVcf:
    type: File
    outputBinding:
      glob: core.vcf

label: snippy-core
requirements:
  - class: DockerRequirement
    dockerPull: 'quay.io/biocontainers/snippy:4.6.0--0'
  - class: InlineJavascriptRequirement