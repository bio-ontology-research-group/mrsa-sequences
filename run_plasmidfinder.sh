for filepath in data/contigs/ID*.fa; do
    sample=$(basename $filepath)
    mkdir data/plasmidfinder/$sample
    docker run -v /home/kulmanm/KAUST/CBRC/mrsa-sequences/data:/data -v /home/kulmanm/KAUST/CBRC/plasmidfinder/plasmidfinder_db/:/database coolmaksat/plasmidfinder -i /data/contigs/$sample -o /data/plasmidfinder/$sample
    echo $sample
done
