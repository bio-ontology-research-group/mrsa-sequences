cwlVersion: v1.1
class: CommandLineTool
inputs:
  genePA: File
outputs:
  svg: stdout
requirements:
  InlineJavascriptRequirement: {}
  DockerRequirement:
    dockerPull: "coolmaksat/circos:latest"
  ResourceRequirement:
    coresMin: 12
    ramMin: $(16 * 1024)
stdout: $(inputs.genePA.nameroot).out
baseCommand: circos
arguments: [$(inputs.genePA),]
