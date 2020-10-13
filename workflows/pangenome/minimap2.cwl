cwlVersion: v1.1
class: CommandLineTool
inputs:
  readsFA: File
outputs:
  readsPAF: stdout
requirements:
  InlineJavascriptRequirement: {}
hints:
  DockerRequirement:
    dockerPull: "quay.io/biocontainers/minimap2:2.17--h8b12597_1"
  ResourceRequirement:
    coresMin: 12
    ramMin: $(16 * 1024)
    outdirMin: $(Math.ceil(inputs.readsFA.size/(1024*1024*1024) + 20))
stdout: $(inputs.readsFA.nameroot).paf
baseCommand: minimap2
arguments: [-c, -X,
            $(inputs.readsFA),
            $(inputs.readsFA)]
