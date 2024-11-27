import pandas as pd
import click as ck
from collections import deque


@ck.command()
def main():
    sim = {}
    with open('data/mecas.sim') as f:
        for line in f:
            it = line.strip().split('\t')
            p1, p2, score = it[0], it[1], float(it[3]) / 100.0
            if p1 == p2:
                continue
            # if score < 0.5:
            #     continue
            if p1 not in sim:
                sim[p1] = []
            if p2 not in sim:
                sim[p2] = []
            sim[p1].append(p2)
            sim[p2].append(p1)

    samples = sim.keys()
    used = set()
    def dfs(prot):
        stack = deque()
        stack.append(prot)
        used.add(prot)
        prots = []
        while len(stack) > 0:
            prot = stack.pop()
            prots.append(prot)
            used.add(prot)
            if prot in sim:
                for p in sim[prot]:
                    if p not in used:
                        used.add(p)
                        stack.append(p)
        return prots

    groups = []
    for p in samples:
        if p not in used:
            group = dfs(p)
            groups.append(group)
    print(groups)

    
if __name__ == '__main__':
    main()
