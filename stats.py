import pandas as pd
import numpy as np
import click as ck
from matplotlib import pyplot as plt
from collections import Counter
from analyzer.constants import bad_samples
from scipy.stats import entropy, wasserstein_distance

ck.command()
def main():
    
    df = pd.read_pickle('data/lab_resistance.pkl')
    drugs = set()
    locations = {}
    total = Counter()
    for row in df.itertuples():
        if row.samples in bad_samples:
            continue
        for d, m in row.resistance:
            if row.location not in locations:
                locations[row.location] = Counter()
            locations[row.location][d] += 1
            drugs.add(d)
    drugs = list(drugs)
    drugs_ind = {v:k for k, v in enumerate(drugs)}
    probs = {}
    for c in locations:
        probs[c] = np.zeros(len(drugs), dtype=np.float32)
        for d, cnts in locations[c].items():
            probs[c][drugs_ind[d]] = cnts
        probs[c] /= np.sum(probs[c])
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
