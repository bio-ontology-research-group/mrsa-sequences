import pandas as pd
import click as ck
import os


@ck.command()
def main():
    #save_data()
    res_df = pd.read_pickle('data/deeparg.pkl')
    for dc in set(res_df['predicted_ARG-class']):
        print(dc)
    with open('data/sample.ids') as f:
        ids = f.read().splitlines()
    drugs = {}
    genes = {}
    for i, row in res_df.iterrows():
        sid = row['sample_id']
        if sid not in drugs:
            drugs[sid] = set()
            genes[sid] = set()
        drugs[sid].add(row['predicted_ARG-class'])
    
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
            
    df = pd.DataFrame({'UID': ids, 'drugs': drug_list})
    df.to_csv('data/deeparg-drugs.csv')

def save_data():
    files = os.listdir('data/deeparg')
    dfs = []
    for filename in files:
        if filename.endswith('.ARG'):
            df = pd.read_csv('data/deeparg/' + filename, sep='\t')
            sample_id = filename.split('.')[0]
            df['sample_id'] = [sample_id] * len(df)
            dfs.append(df)
    df = pd.concat(dfs)
    print(df)
    df.to_pickle('data/deeparg.pkl')
    
if __name__ == '__main__':
    main()
