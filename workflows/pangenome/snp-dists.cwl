cwlVersion: v1.1
class: CommandLineTool
inputs:
  alignments: File
outputs:
  distances: stdout
requirements:
  InlineJavascriptRequirement: {}
  DockerRequirement:
    dockerPull: "quay.io/biocontainers/snp-dists:0.7.0--hed695b0_0"
  ResourceRequirement:
    coresMin: 12
    ramMin: $(16 * 1024)
stdout: $(inputs.alignments.nameroot).tab
baseCommand: snp-dists
arguments: [$(inputs.alignments),]
