for i in $(seq 872 873); do
    a=$(printf "%03d" $i)
    echo "Uploading sample $a"
    python main.py -sr1 ~/data_mrsa/all_samples/ID00${a}_R1.fastq.gz -sr2 ~/data_mrsa/all_samples/ID00${a}_R2.fastq.gz -m ../data/metadata/ID00${a}.yaml
done
