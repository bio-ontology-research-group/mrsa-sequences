import pandas as pd
import numpy as np
import click as ck
from collections import Counter
from analyzer.constants import bad_samples
import matplotlib.pyplot as plt
import seaborn as sns

ck.command()
def main():
    plot_sequence_types()

def plot_sequence_types():
    df = pd.read_csv('data/cleanmrsa.csv', sep=',')
    df['val'] = [1] * len(df)
    df = df[df['species'] == 'Staphylococcus aureus']
    print(len(df))

    # locations = df['geolocation']
    # seq_types = df['ST']
    data = {}
    all_types = set()
    for row in df.itertuples():
        if row.geolocation not in data:
            data[row.geolocation] = Counter()
        data[row.geolocation][str(row.ST)] += 1
        all_types.add(str(row.ST))
    all_types = sorted(list(all_types))
    locations = []
    seq_types = []
    number = []
    for loc, stypes in data.items():
        for st in all_types:
            locations.append(loc)
            seq_types.append(st)
            number.append(stypes[st])

    data_df = pd.DataFrame({'Location': locations, 'Sequence Type': seq_types, 'Number': number})
    sns.set_theme()
    # Load the example flights dataset and convert to long-form
    seq_types = data_df.pivot("Location", "Sequence Type", "Number")
    # Draw a heatmap with the numeric values in each cell
    f, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(seq_types, annot=True, fmt="d", linewidths=.5, ax=ax)
    plt.savefig('/home/kulmanm/data/seq_types.png')
    
    
def plot_resistance():
    plt.rcdefaults()
    
    df = pd.read_pickle('data/lab_resistance.pkl')

    drugs = {}
    total = Counter()
    for row in df.itertuples():
        if row.samples in bad_samples:
            print(row.samples)
            continue
        for d, m in row.resistance:
            if row.location not in drugs:
                drugs[row.location] = Counter()
            drugs[row.location][d] += 1
            total[d] += 1
    print(len(df))
    all_drugs = list(total.keys())
    for d, cnt in drugs.items():
        locations = dict(cnt.most_common())
        y_pos = np.arange(len(all_drugs))
        samples = [locations[d] if d in locations else 0 for d in all_drugs]
        fig, ax = plt.subplots()
        ax.barh(y_pos, samples, align='center')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(all_drugs)
        #ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Number of samples')
        # ax.set_title(f'False negatives. Positive in lab, not in genotype ({fnn})')
        ax.set_title(f'Resistance by drugs for {d}')
        plt.tight_layout()
        d = d.replace('/', '_')
        plt.savefig(f'/home/kulmanm/data/{d}.png')


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
