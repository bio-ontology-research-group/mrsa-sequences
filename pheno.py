import pandas as pd
import click as ck
import numpy as np

@ck.command()
def main():
    df = pd.read_csv('data/traits.csv')
    drugs = list(df.columns[1:])
    drugs.remove('Linezolid')
    drugs.remove('Teicoplanin')
    drugs.remove('Tigecycline')
    drugs.remove('Vancomycin')
    for d in drugs:
        pos = []
        neg = []
        for i, row in df.iterrows():
            if row[d]:
                pos.append(row.ID)
            else:
                neg.append(row.ID)
        n = min(len(pos), len(neg))
        pos, neg = np.array(pos), np.array(neg)
        np.random.shuffle(pos)
        pos = pos[:n]
        np.random.shuffle(neg)
        neg = neg[:n]
        with open(f'data/{d}.phe', 'w') as f:
            for sid in pos:
                f.write(f'{sid}\t{sid}\t2\n')
            for sid in neg:
                f.write(f'{sid}\t{sid}\t1\n')


if __name__ == '__main__':
    main()
