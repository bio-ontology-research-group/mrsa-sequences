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
  alignment:
    type: File
    outputSource: snippyCore/alignments
  alignmentStats:
    type: File
    outputSource: snippyCore/outputTxt
  snp_dists:
    type: File
    outputSource: snpDists/distances
  pangenome:
    type: File
    outputSource: roary/pangenome
  gene_presence_absence:
    type: File
    outputSource: roary/gene_presence_absence
  pangenome_stats:
    type: File
    outputSource: roary/statistics
  treefile:
    type: File
    outputSource: iqTree/result_tree
  iqtree_report:
    type: File
    outputSource: iqTree/report
  # augur:
  #   type: File
  #   outputSource: augur_export/out_file
  # gfa:
  #   type: File
  #   outputSource: induceGraph/seqwishGFA
  # odgi:
  #   type: File
  #   outputSource: vizGraph/odgiPNG
  pangenome_svg:
    type: File
    outputSource: roary2svg/svg
steps:
  snippyCore:
    in:
      dirs: dirs
      reference: reference
      inprefix: snippy_inprefix
    out: [alignments,outputVcf,outputTxt]
    run: snippy-core.cwl
  iqTree:
    in:
      alignments: snippyCore/alignments
    out: [result_tree,report]
    run: iqtree.cwl
  roary:
    in:
      gff_files: gff_files
    out: [gene_presence_absence,pangenome,statistics]
    run: roary.cwl
  # augur_refine:
  #   in:
  #     alignment: snippyCore/alignments
  #     tree_raw: iqTree/result_tree
  #     metadata: metadata
  #   out:
  #     [out_tree, out_node_data]
  #   run: augur_refine.cwl
  # augur_traits:
  #   in:
  #     tree: augur_refine/out_tree
  #     metadata: metadata
  #   out: [traits]
  #   run: augur_traits.cwl
  # augur_ancestral:
  #   in:
  #     tree: augur_refine/out_tree
  #     alignment: snippyCore/alignments
  #   out: [nt_muts]
  #   run: augur_ancestral.cwl
  # augur_translate:
  #   in:
  #     tree: augur_refine/out_tree
  #     ancestral: augur_ancestral/nt_muts
  #     reference: reference_gb
  #   out: [aa_muts]
  #   run: augur_translate.cwl
  # augur_export:
  #   in:
  #     tree: augur_refine/out_tree
  #     metadata: metadata
  #     node_data: [augur_refine/out_node_data,augur_traits/traits,augur_ancestral/nt_muts,augur_translate/aa_muts]
  #   out: [out_file]
  #   run: augur_export.cwl
  # overlapReads:
  #   in: {readsFA: snippyCore/alignments}
  #   out: [readsPAF]
  #   run: minimap2.cwl
  # induceGraph:
  #   in:
  #     readsFA: snippyCore/alignments
  #     readsPAF: overlapReads/readsPAF
  #   out: [seqwishGFA]
  #   run: seqwish.cwl
  # buildGraph:
  #   in: {inputGFA: induceGraph/seqwishGFA}
  #   out: [odgiGraph]
  #   run: odgi-build.cwl
  # vizGraph:
  #   in: {inputODGI: buildGraph/odgiGraph}
  #   out: [odgiPNG]
  #   run: odgi-viz.cwl
  snpDists:
    in:
      alignments: snippyCore/alignments
    out: [distances]
    run: snp-dists.cwl
  roary2svg:
    in:
      genePA: roary/gene_presence_absence
    out: [svg]
    run: roary2svg.cwl