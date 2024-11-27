import click as ck
import math
import os
import numpy as np
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from analyzer.constants import bad_samples

@ck.command()
def main():
    files = [f for f in os.listdir('data/contigs') if f.endswith('.fa')]
    files = [f for f in files if f.split('.')[0] not in bad_samples][:10]
    print(files)
    
    with open('seqs.fa', 'w') as w:
        for fn in files:
            sid = fn.split('.')[0]
            with open(f'data/contigs/{fn}', 'r') as f:
                sequences = SeqIO.parse(f, 'fasta')
                for rec in sequences:
                    rec.id = f'{sid}|{rec.id}'
                    SeqIO.write(rec, w, 'fasta')


if __name__ == '__main__':
    main()
