#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.0

label: snippy-core
requirements:
  - class: DockerRequirement
    dockerPull: 'quay.io/biocontainers/snippy:4.6.0--0'
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    coresMin: 1
    coresMax: 2

baseCommand: snippy-core

inputs:
  reference:
    type: File
    inputBinding:
      position: 1
      prefix: '--ref'
    label: 'Reference genome. Supports FASTA, GenBank, EMBL (not GFF) (default '''')'
  dirs:
    type: Directory[]
    inputBinding:
      position: 2
    label: 'Output dirs from snippy'
  inprefix:
    type: string?
    default: 'snps'
    inputBinding:
      position: 1
      prefix: '--inprefix'

outputs:
  alignments:
    type: File
    outputBinding:
      glob: core.full.aln
  outputVcf:
    type: File
    outputBinding:
      glob: core.vcf

