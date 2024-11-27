import pandas as pd
import numpy as np
import click as ck
import os
import json


@ck.command()
def main():
    with open('data/sample.ids') as f:
        ids = f.read().splitlines()
    plasmids = []
    for sid in ids:
        filepath = f'data/plasmidfinder/{sid}.fa/data.json'
        if not os.path.exists(filepath):
            plasmids.append('')
            continue
        with open(filepath) as f:
            data = json.loads(f.read())
            enteros = data['plasmidfinder']['results']['Enterobacteriales']
            gram_positive = data['plasmidfinder']['results']['Gram Positive']
            res = []
            for plasmid, hits in gram_positive.items():
                if hits == 'No hit found':
                    continue
                for hit, values in hits.items():
                    res.append(values['plasmid'])
        plasmids.append('; '.join(res))
    df = pd.DataFrame({'UID': ids, 'plasmids': plasmids})
    df.to_csv('data/plasmidfinder.csv')
    

if __name__ == '__main__':
    main()
