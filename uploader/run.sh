for i in $(seq 003 094); do
    a=$(printf "%03d" $i)
    echo "Uploading sample $a"
    python main.py -sr1 /opt/data-mrsa/reads/MRSA${a}_R1.fastq.gz -sr2 /opt/data-mrsa/reads/MRSA${a}_R2.fastq.gz -m /opt/data-mrsa/metadata/MRSA${a}.json
done
