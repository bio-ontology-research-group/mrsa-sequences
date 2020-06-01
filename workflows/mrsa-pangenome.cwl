cwlVersion: v1.1
class: Workflow
requirements:
  MultipleInputFeatureRequirement: {}
inputs:
  dirs: Directory[]
  snippy_ref: File
  gff_files: File[]
outputs:

steps:
  snippyCore:
    in:
      dirs: dirs
      ref: snippy_ref
    out: []
    run: snippy_core.cwl
  iqTree:
    in:
    out: []
    run: iqtree.cwl
  roary:
    in:
    out: []
    run: roary.cwl

$namespaces:
  edam: http://edamontology.org/
  s: http://schema.org/
