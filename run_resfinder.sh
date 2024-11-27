for i in $(seq 840 872); do
    echo $sample
    filepath=data/condigs/ID00${i}.fa
    sample=$(basename $filepath)
    docker run -v /home/kulmanm/KAUST/CBRC/mrsa-sequences/data:/data -v /home/kulmanm/KAUST/CBRC/resfinder/db_resfinder/:/usr/src/db_resfinder -v /home/kulmanm/KAUST/CBRC/resfinder/db_pointfinder/:/usr/src/db_pointfinder coolmaksat/resfinder --inputfasta /data/contigs/$sample -acq -c --species staphylococcus_aureus > data/resfinder4.0/$sample.txt
done
