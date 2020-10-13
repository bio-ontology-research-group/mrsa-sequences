cwlVersion: v1.1
class: CommandLineTool
inputs:
  readsFA: File
  readsPAF: File
outputs:
  seqwishGFA:
    type: File
    outputBinding:
      glob: $(inputs.readsPAF.nameroot).gfa
requirements:
  InlineJavascriptRequirement: {}
hints:
  DockerRequirement:
    dockerPull: "quay.io/biocontainers/seqwish:0.4.1--h8b12597_0"
  ResourceRequirement:
    coresMin: 8
    ramMin: $(32 * 1024)
    outdirMin: $(Math.ceil(inputs.readsFA.size/(1024*1024*1024) + 20))
baseCommand: seqwish
arguments: [-s, $(inputs.readsFA),
            -p, $(inputs.readsPAF),
            -g, $(inputs.readsPAF.nameroot).gfa]
