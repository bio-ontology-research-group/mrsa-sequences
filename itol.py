import pandas as pd
import numpy as np

def main():
    df = pd.read_csv('data/metadata.csv', sep='\t')

    colors = {
        'Alhasa ': '#C0C0C0',
        'Hail': '#000000',
        'Jeddah': '#FF0000',
        'Madina': '#00FF00',
        'Makkah': '#FFFF00',
        'Riyadh': '#0000FF',
        'Jazan': '#FF00FF',
    
    }
    for row in df.itertuples():
        loc = row.geolocation.strip()
        if loc not in colors:
            continue
        c = colors[loc]
        sid = row.UID
        print(sid, c, loc)


if __name__ == '__main__':
    main()
