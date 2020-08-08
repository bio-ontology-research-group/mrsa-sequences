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
  reference_gb: File
  gff_files: File[]
  snippy_inprefix: string
  metadata: File

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
  augur:
    type: File
    outputSource: augur_export/out_file

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
  augur_refine:
    in:
      alignment: snippyCore/alignments
      tree_raw: iqTree/result_tree
      metadata: metadata
    out:
      [out_tree, out_node_data]
    run: augur_refine.cwl
  augur_traits:
    in:
      tree: augur_refine/out_tree
      metadata: metadata
    out: [traits]
  augur_ancestral:
    in:
      tree: augur_refine/out_tree
      alignment: snippyCore/alignments
    out: [nt_muts]
    run: augur_ancestral.cwl
  augur_translate:
    in:
      tree: augur_refine/out_tree
      ancestral: augur_ancestral/nt_muts
      reference: reference_gb
    out: [aa_muts]
    run: augur_translate.cwl
  augur_export:
    in:
      tree: augur_refine/out_tree
      metadata: metadata
      node_data: [augur_refine/out_node_data,augur_traits/traits,augur_ancestral/nt_muts,augur_translate/aa_muts]
    out: [out_file]
    run: augur_export.cwl
