import pandas as pd
import numpy as np
import click as ck
from matplotlib import pyplot as plt
from collections import Counter

ck.command()
def main():
    plt.rcdefaults()
    fig, ax = plt.subplots()
    
    # drugs
    
    df = pd.read_pickle('data/resistance.pkl')
    df = load_card(df)
    res_drugs = df['card_drugs']
    # res_drugs = []
    # fpn = 0
    # tpn = 0
    # fnn = 0
    # for row in df.itertuples():
    #     tp = set(row.genotype).intersection(row.labs_resist)
    #     fp = set(row.genotype).intersection(row.labs_sensitive)
    #     fn = set(row.labs_resist) - set(row.genotype)
    #     tpn += len(tp)
    #     fpn += len(fp)
    #     fnn += len(fn)
    #     res_drugs.append(fn)
    
    drugs = Counter()
    for ds in res_drugs:
        drugs.update(ds)

    drugs = dict(drugs.most_common())
    drug_names = list(drugs.keys())
    for i in range(len(drug_names)):
        if drug_names[i] == 'Trimethoprim/Sulfamethoxazole':
            drug_names[i] = 'Trimethoprim'
        elif drug_names[i].find('+') != -1:
            drug_names[i] = drug_names[i].split('+')[0]
    y_pos = np.arange(len(drugs))
    samples = drugs.values()
    
    ax.barh(y_pos, samples, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(drug_names)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Number of samples')
    # ax.set_title(f'False negatives. Positive in lab, not in genotype ({fnn})')
    ax.set_title(f'CARD database drugs')
    plt.tight_layout()
    plt.savefig('/opt/data/card.png')


def load_card(df):
    card_drugs = []
    all_dfs = []
    for i, row in df.iterrows():
        s_id = row['samples']
        drugs = set()
        # if os.path.exists(f'data/contigs/{s_id}.fa.out.txt'):
        cdf = pd.read_csv(f'data/contigs/{s_id}.fa.out.txt', delimiter='\t')
        for ds in cdf['Drug Class']:
            drugs |= set(ds.split('; '))
        card_drugs.append(drugs)
        samples = [s_id] * len(cdf)
        cdf['samples'] = samples
        all_dfs.append(cdf)
    df['card_drugs'] = card_drugs
    adf = pd.concat(all_dfs, ignore_index=True)
    adf.to_pickle('data/card.pkl')
    return df

if __name__ == '__main__':
    main()
