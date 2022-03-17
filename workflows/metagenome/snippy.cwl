#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.0

label: snippy
requirements:
  - class: DockerRequirement
    dockerPull: 'quay.io/biocontainers/snippy:4.6.0--0'
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    ramMin: 30000 
    coresMin: 2

baseCommand: snippy

inputs:
  reference:
    type: File
    inputBinding:
      position: 2
      prefix: '--reference'
    label: 'Reference genome. Supports FASTA, GenBank, EMBL (not GFF) (default '''')'
  R1:
    type: File?
    inputBinding:
      position: 2
      prefix: '--R1'
  R2:
    type: File?
    inputBinding:
      position: 4
      prefix: '--R2'
    label: 'Reads, paired-end R2 (right) (default '''')'
  contigs:
    type: File?
    inputBinding:
      position: 4
      prefix: '--ctgs'
    label: Don't have reads use these contigs (default '')
  pe_interleaved:
    type: File?
    inputBinding:
      position: 4
      prefix: '--peil'
  bam:
    type: File?
    inputBinding:
      position: 4
      prefix: '--bam'
    label: Use this BAM file instead of aligning reads (default '')
  targets:
    type: File?
    inputBinding:
      position: 4
      prefix: '--targets'
    label: Only call SNPs from this BED file (default '')
  subsample:
    type: float?
    inputBinding:
      position: 4
      prefix: '--subsample'
    label: Subsample FASTQ to this proportion (default '1')
  mapping_qual:
    type: int?
    inputBinding:
      position: 5
      prefix: '--mapqual'
    label: Minimum read mapping quality to consider (default '60')
  base_quality:
    type: int?
    inputBinding:
      position: 5
      prefix: '--basequal'
    label: Minimum base quality to consider (default '13')
  min_coverage:
    type: int?
    inputBinding:
      position: 5
      prefix: '--mincov'
    label: Minimum site depth to for calling alleles (default '10')
  min_fraction:
    type: float?
    inputBinding:
      position: 5
      prefix: '--minfrac'
    label: Minumum proportion for variant evidence (0=AUTO) (default '0')
  min_qual:
    type: float?
    inputBinding:
      position: 5
      prefix: '--minqual'
    label: Minumum QUALITY in VCF column 6 (default '100')
  max_soft_clipping:
    type: int?
    inputBinding:
      position: 5
      prefix: '--maxsoft'
    label: Maximum soft clipping to allow (default '10')
  bwa_options:
    type: string?
    inputBinding:
      position: 3
      prefix: '--bwaopt'
    label: 'Extra BWA MEM options, eg. -x pacbio (default '''')'
  freebayes_options:
    type: string?
    inputBinding:
      position: 5
      prefix: '--fbopt'
    label: 'Extra Freebayes options, eg. --theta 1E-6 --read-snp-limit 2 (default '''')'
  outdir:
    type: string?
    default: 'snippy'
    inputBinding:
      position: 1
      prefix: '--outdir'
    label: Output folder (default '')
  prefix:
    type: string?
    default: 'snps'
    inputBinding:
      position: 1
      prefix: '--prefix'
    label: Prefix for output files (default 'snps')
  report:
    type: boolean?
    inputBinding:
      position: 1
      prefix: '--report'
    label: Produce report with visual alignment per variant (default OFF)
  cleanup:
    type: boolean?
    inputBinding:
      position: 1
      prefix: '--cleanup'
    label: Remove most files not needed for snippy-core (inc. BAMs!) (default OFF)
  rgid:
    type: string?
    inputBinding:
      position: 1
      prefix: '--rgid'
    label: 'Use this @RG ID: in the BAM header (default '''')'
  unmapped:
    type: boolean?
    inputBinding:
      position: 1
      prefix: '--unmapped'
    label: Keep unmapped reads in BAM and write FASTQ (default OFF)
  force:
    type: boolean?
    inputBinding:
      position: 2
      prefix: '--force'
    label: Force overwrite of existing output folder (default OFF)
  quiet:
    type: boolean?
    inputBinding:
      position: 2
      prefix: '--quiet'
    label: No screen output (default OFF)
  version:
    type: boolean?
    inputBinding:
      position: 2
      prefix: '--version'
    label: Print version and exit
  citation:
    type: boolean?
    inputBinding:
      position: 2
      prefix: '--citation'
    label: Print citation for referencing snippy
  cpus:
    type: int?
    inputBinding:
      position: 3
      prefix: '--cpus'
    label: Maximum number of CPU cores to use (default '8')
  ram:
    type: float?
    default: 16
    inputBinding:
      position: 3
      prefix: '--ram'
    label: Try and keep RAM under this many GB (default '16')
  tmp:
    type: Directory?
    inputBinding:
      position: 3
      prefix: '--tmp'
    label: Fast temporary storage eg. local SSD (default '/tmp')
outputs:
  tab_output:
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).tab
  txt_output:
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).txt
  csv_output:
    label: A comma-separated version of the .tab file .html
    type: File
    outputBinding:
      glob: |
        $(inputs.outdir)/$(inputs.prefix).csv
  html_output:
    label: A HTML version of the .tab file
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).html
  vcf_output:
    label: The final annotated variants in VCF format
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).vcf
  bed_output:
    label: The variants in BED format
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).bed
  gff3_output:
    label: The variants in GFF3 format
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).gff
  bam_output:
    label: >-
      The alignments in BAM format. Includes unmapped, multimapping reads.
      Excludes duplicates.
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).bam
    secondaryFiles:
      - $(inputs.outdir)/$(inputs.prefix).bam.bai
  log_output:
    label: A log file with the commands run and their outputs
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).log
  aligned_fasta_output:
    label: >-
      A version of the reference but with - at position with depth=0 and N for 0
      < depth < --mincov (does not have variants)
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).aligned.fa
  consensus_fasta_output:
    label: A version of the reference genome with all variants instantiated
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).consensus.fa
  consensus_substitutions_fasta_output:
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).consensus.subs.fa
  raw_vcf:
    label: The unfiltered variant calls from Freebayes
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).raw.vcf
  filtered_vcf:
    label: The filtered variant calls from Freebayes
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).raw.vcf
  compressed_vcf:
    label: Compressed .vcf file via BGZIP
    type: File
    outputBinding:
      glob: $(inputs.outdir)/$(inputs.prefix).vcf.gz
    secondaryFiles:
      - '$(inputs.outdir)/$(inputs.prefix).vcf,gz,csi'
  out_directory:
    label: Output directory
    type: Directory
    outputBinding:
      glob: $(inputs.outdir)
  