cwlVersion: v1.1
class: CommandLineTool
inputs:
  genePA: File
outputs:
  svg: stdout
requirements:
  InlineJavascriptRequirement: {}
  DockerRequirement:
    dockerPull: "coolmaksat/roary2svg:latest"
  ResourceRequirement:
    coresMin: 12
    ramMin: $(16 * 1024)
stdout: $(inputs.genePA.nameroot).svg
baseCommand: roary2svg.pl
arguments: [$(inputs.genePA),]
