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
    dockerPull: quay.io/biocontainers/prokka:1.14.6--pl526_0  

baseCommand: prokka

inputs:
  fa_file:
    type: File
    inputBinding:
      position: 1
  outdir:
    type: string?
    default: 'prokka'
    inputBinding:
      position: 1
      prefix: '--outdir'
    label: Output folder (default '')
  prefix:
    type: string?
    default: 'prokka'
    inputBinding:
      position: 1
      prefix: '--prefix'
    label: Prefix for output files (default 'prokka')
  kingdom:
    type: string?
    default: 'Bacteria'
    inputBinding:
      position: 1
      prefix: '--kingdom'
  force:
    type: boolean?
    inputBinding:
      position: 2
      prefix: '--force'
    label: Force overwrite of existing output folder (default OFF)
  cpus:
    type: int?
    inputBinding:
      position: 1
      prefix: '--cpus'
  locustag:
    type: string?
    inputBinding:
      position: 1
      prefix: '--locustag'
  

outputs:
  gff_output:
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).gff
  faa_output:
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).faa
  out_directory:
    label: Output directory
    type: Directory
    outputBinding:
      glob: $(inputs.outdir)
