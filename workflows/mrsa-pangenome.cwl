cwlVersion: v1.1
class: Workflow
requirements:
  ResourceRequirement:
    ramMin: 8000
    coresMin: 1
  MultipleInputFeatureRequirement: {}
  
inputs:
  dirs: Directory[]
  reference: File
  gff_files: File[]
  snippy_inprefix: string
outputs:
  pangenome:
    type: File
    outputSource: roary/pangenome
  treefile:
    type: File
    outputSource: iqTree/result_tree
  iqtree:
    type: File
    outputSource: iqTree/report


steps:
  snippyCore:
    in:
      dirs: dirs
      reference: reference
      inprefix: snippy_inprefix
    out: [alignments,outputVcf]
    run: snippy-core.cwl
  iqTree:
    in:
      alignments: snippyCore/alignments
    out: [result_tree,report]
    run: iqtree.cwl
  roary:
    in:
      gff_files: gff_files
    out: [gene_presence_absence,pangenome]
    run: roary.cwl
