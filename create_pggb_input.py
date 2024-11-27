import pandas as pd
import numpy as np
import click as ck
from matplotlib import pyplot as plt
from collections import Counter
from analyzer.constants import bad_samples
from scipy.stats import entropy, wasserstein_distance
from Bio import SeqIO
import os
from pathlib import Path
import gzip

ck.command()
def main():
    data_root = Path('data/refseq/bacteria')
    ref_dirs = list(data_root.iterdir())
    np.random.shuffle(ref_dirs)
    ref_dirs = ref_dirs[:100]
    with open('data/refseq/in.fa', 'w') as w:
        for ref in ref_dirs:
            seq_file = list(ref.glob('*.fna.gz'))[0]
            with gzip.open(seq_file, 'rt') as f:
                seqs = SeqIO.parse(f, 'fasta')
                SeqIO.write(seqs, w, 'fasta')
            
if __name__ == '__main__':
    main()
