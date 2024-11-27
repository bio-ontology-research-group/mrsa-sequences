import click as ck
import pandas as pd
import numpy as np


@ck.command()
def main():
    df = pd.read_csv('data/locations.tsv', sep='\t')
    colors = {
        'Riyadh': '#0275d8',
        'Alhasa': '#5cb85c',
        'Jeddah': '#5bc0de',
        'Makkah': '#f0ad4e',
        'Madina': '#d9534f',
        'Hail': '#292b2c'
    }

    for i, row in enumerate(df.itertuples()):
        sid = row.UID.replace('ID00', 'MRSA')
        loc = row.geolocation.strip()
        if loc not in colors:
            continue
        print(sid, 'label', colors[loc], 'bold 2')

if __name__ == '__main__':
    main()

