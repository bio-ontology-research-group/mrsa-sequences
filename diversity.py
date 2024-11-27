import pandas as pd
import numpy as np
import click as ck
#from matplotlib import pyplot as plt
from collections import Counter
from analyzer.constants import bad_samples
from scipy.stats import entropy, wasserstein_distance
from skbio.diversity import beta_diversity, alpha_diversity

ck.command()
def main():
    
    df = pd.read_csv('data/cleanmrsa.csv')
    print(df['geolocation'])
    stypes = set()
    locations = {}
    total = Counter()
    for row in df.itertuples():
        if row.UID in bad_samples:
            continue
        if row.geolocation not in locations:
            locations[row.geolocation] = Counter()
        locations[row.geolocation][row.ST] += 1
        stypes.add(row.ST)
    stypes = list(stypes)
    stypes_ind = {v:k for k, v in enumerate(stypes)}
    probs = {}
    data = np.zeros((len(locations), len(stypes)), dtype=np.int32)
    
    ids = list(locations.keys())
    
    for i, c in enumerate(ids):
        probs[c] = np.zeros(len(stypes), dtype=np.float32)
        for d, cnts in locations[c].items():
            probs[c][stypes_ind[d]] = cnts
            data[i, stypes_ind[d]] = cnts
        print(c, np.sum(probs[c]))
        probs[c] /= np.sum(probs[c])
        
    adiv_obs_otus = alpha_diversity('observed_otus', data, ids)
    print(adiv_obs_otus)
    bc_dm = beta_diversity("braycurtis", data, ids)
    print(bc_dm)
    #return
    locs = list(locations.keys())
    dists = []
    for i in range(len(locs)):
        for j in range(i + 1, len(locs)):
            dists.append((locs[i] + '-' + locs[j], wasserstein_distance(probs[locs[i]], probs[locs[j]])))
    dists = sorted(dists, key=lambda x: x[1])
    for pair, dist in dists:
        print(pair, dist)

if __name__ == '__main__':
    main()
