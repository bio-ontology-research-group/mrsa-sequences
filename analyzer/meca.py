import pandas as pd
import click as ck
import numpy as np
import os
import json

@ck.command()
def main():
    group_mecas()
    
def group_mecas():
    with open('data/mec_groups.json') as f:
        groups = json.loads(f.read())
    mecas = read_fasta('data/mecas.fa')
    group1 = set(groups['groups'][0])
    group2 = set(groups['groups'][1])
    with open('data/mecas_group1.fa', 'w') as f:
        for sample_id, seq in mecas.items():
            if sample_id in group1:
                f.write(f'>{sample_id}\n{seq}\n')
    with open('data/mecas_group2.fa', 'w') as f:
        for sample_id, seq in mecas.items():
            if sample_id in group2:
                f.write(f'>{sample_id}\n{seq}\n')
    
    
def save_mecas():
    df = pd.read_pickle('data/gt_resistance.pkl')
    #genes = set(df['PRODUCT'].values)
    df = df[df['PRODUCT'] == 'mecA']
    for row in df.itertuples():
        sample_id = row.samples
        contig = row.SEQUENCE
        gene = row.GENE
        s = int(row.START)
        e = int(row.END)
        filename = f'data/contigs/{sample_id}.fa'
        if os.path.exists(filename):
            seqs = read_fasta(filename)
            seq = seqs[contig]
            mec = seq[s - 1:e]
            with open(f'data/mecas/{sample_id}.fa', 'w') as w:
                w.write(f'>{sample_id}\n{mec}\n')
    
def read_fasta(filename):
    res = {}
    seq = ''
    inf = ''
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if seq != '':
                    res[inf] = seq
                    seq = ''
                inf = line[1:]
            else:
                seq += line
        res[inf] = seq
    return res


if __name__ == '__main__':
    main()
