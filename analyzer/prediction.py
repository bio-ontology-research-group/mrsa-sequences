import click as ck
import pandas as pd
import numpy as np


@ck.command()
@ck.option('--gene-presence-absence', '-gpa', default='data/gene_presence_absence.pkl',)
def main(gene_presence_absence):
    df = pd.read_pickle(gene_presence_absence)
    df = df[df['No. isolates'] >= 10]
    df = df[df['No. isolates'] < 351]
    data = df.values[:, 14:].transpose()
    
    print((data.astype(np.str) == 'nan').astype(np.int32))

if __name__ == '__main__':
    main()
