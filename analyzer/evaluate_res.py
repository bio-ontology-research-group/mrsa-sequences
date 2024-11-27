import click as ck
import pandas as pd
import numpy as np
from constants import bad_samples


@ck.command()
def main():
    df = pd.read_csv('data/traits.tsv')
    res_df = pd.read_pickle('data/gt_resfinder.pkl')
    print(res_df)
    res = {}
    all_drugs = set()
    for row in res_df.itertuples():
        sid = row.sample_id
        drugs = set(row.drugs.split(', '))
        if sid not in res:
            res[sid] = set()
        res[sid] |= drugs
        all_drugs |= drugs
    print(all_drugs)
    df.rename(columns = {
        'Benzylpenicillin':'Penicillin',
        'Trimethoprim/Sulfamethoxazole': 'Trimethoprim',
        'Fusidic Acid': 'Fusidic acid'}, inplace = True)
    drugs = list(df.columns)
    drugs = drugs[1:]
    for drug in drugs:
        tp = 0
        fp = 0
        fn = 0
        prec = 0
        rec = 0
        for i, row in df.iterrows():
            sid = row[0]
            if sid in bad_samples:
                continue
            label = row[drug]
            pred = int(sid in res and drug in res[sid])
            if label == 1 and pred == 1:
                tp += 1
            elif label == 1:
                fn += 1
            elif pred == 1:
                fp += 1
            if tp == 0:
                continue
            prec = tp / (tp + fp)
            rec = tp / (tp + fn)
            fscore = 2 * prec * rec / (prec + rec)
        if prec != 0.0:
            print(f'{drug} & {prec:.3f} & {rec:.3f} & {fscore:.3f} \\\\')
            print('\\hline')
            
if __name__ == '__main__':
    main()
