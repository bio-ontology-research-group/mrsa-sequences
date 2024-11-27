for filepath in data/contigs/ID00534.fa; do
    sample=$(basename $filepath)
    echo $sample
    docker run -v /home/kulmanm/KAUST/CBRC/mrsa-sequences/data:/data quay.io/biocontainers/rgi:5.1.1--py_0 rgi main -i /data/contigs/$sample -o /data/card_results/$sample
done
