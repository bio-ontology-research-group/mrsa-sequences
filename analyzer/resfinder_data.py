import pandas as pd
import numpy as np
import click as ck
import os


@ck.command()
def main():
    save_resistance()
    res_df = pd.read_pickle('data/gt_resfinder.pkl')
    with open('data/sample.ids') as f:
        ids = f.read().splitlines()
    drugs = {}
    genes = {}
    for row in res_df.itertuples():
        sid = row.sample_id
        if sid not in drugs:
            drugs[sid] = set()
            genes[sid] = set()
        drugs[sid] |= set(row.drugs.split(', '))
        genes[sid].add(row.gene.split('_')[0])

    drug_list = []
    gene_list = []
    for sid in ids:
        if sid in drugs:
            drug_list.append('; '.join(drugs[sid]))
        else:
            drug_list.append('')
        if sid in genes:
            gene_list.append('; '.join(genes[sid]))
        else:
            gene_list.append('')
            
    df = pd.DataFrame({'UID': ids, 'drugs': drug_list, 'genes': gene_list})
    df.to_csv('data/resfinder-drugs.csv')
    
def save_resistance():
    resistance = load_resistance()
    files = os.listdir('data/resfinder4.0')
    samples = []
    contigs = []
    drugs = []
    drug_classes = []
    starts = []
    ends = []
    scores = []
    genes = []
    for filename in files:
        sample_id, infos = load_data(filename)
        for info in infos:
            contig, pos, gene, score = info[0], info[1], info[2], float(info[3])
            if score < 80:
                continue
            if gene not in resistance:
                continue
            samples.append(sample_id)
            contigs.append(contig)
            start, end = pos.split('..')
            starts.append(int(start))
            ends.append(int(end))
            genes.append(gene)
            scores.append(score)
            drug_classes.append(resistance[gene][0])
            drugs.append(resistance[gene][1])
    
    df = pd.DataFrame({
        'sample_id': samples,
        'contig': contigs,
        'start': starts,
        'end': ends,
        'gene': genes,
        'drug_class': drug_classes,
        'drugs': drugs,
        'score': scores
    })
    df.to_pickle('data/gt_resfinder.pkl')
    df.to_csv('data/gt_resfinder.csv')

def load_data(filename):
    sample_id = filename.split('.')[0]
    genes = []
    with open(f'data/resfinder4.0/{filename}') as f:
        for line in f:
            line = line.strip()
            if line.startswith('Saving: '):
                info = line[8:].split(':')
                genes.append(info)
    return sample_id, genes

def load_resistance():
    res = {}
    with open(f'../resfinder/db_resfinder/phenotypes.txt') as f:
        next(f)
        for line in f:
            it = line.strip().split('\t')
            gene, drug_class, drugs = it[0], it[1], it[2]
            res[gene] = (drug_class, drugs)
    return res

if __name__ == '__main__':
    main()
