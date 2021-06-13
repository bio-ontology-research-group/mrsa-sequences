import pandas as pd
import click as ck
import numpy as np


@ck.command()
def main():
    df = pd.read_pickle('data/resistance.pkl')
    print(df.columns)
    fpn = 0
    tpn = 0
    fnn = 0
    for row in df.itertuples():
        tp = set(row.genotype).intersection(row.labs_resist)
        fp = set(row.genotype).intersection(row.labs_sensitive)
        fn = set(row.labs_resist) - set(row.genotype)
        tpn += len(tp)
        fpn += len(fp)
        fnn += len(fn)
        print(row.samples, tp, fp, fn, row.genotype)
    print(tpn, fpn, fnn)
if __name__ == '__main__':
    main()
