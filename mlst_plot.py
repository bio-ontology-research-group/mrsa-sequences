import pandas as pd
import json
from collections import Counter
import numpy as np
import csv
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from analyzer.constants import SAMPLES

def main():
    with open('data/colors.txt') as f:
        colors = f.read().strip().split(', ')
    locations = {}
    df = pd.read_csv('data/locations.tsv', sep='\t')
    for row in df.itertuples():
        sid = row.UID
        locations[sid] = row.geolocation.strip()

    data = json.loads(open('data/analysis.json').read())
    cnt_loc = {}
    cnt = Counter()
    stypes = set()
    with open('data/pubmlst.csv', 'w') as f:
        w = csv.writer(f)
        for sid, items in data['mlst']:
            if sid not in SAMPLES: # Ignore bad samples
                continue
            loc = locations[sid]
            row = [sid,] + items + [loc]
            w.writerow(row)
            if loc not in cnt_loc:
                cnt_loc[loc] = Counter()
            if items[0] == 'saureus':
                if items[1] != '-': 
                    cnt_loc[loc][items[1]] += 1
                    cnt[items[1]] += 1
                    stypes.add(items[1])
                else:
                    cnt_loc[loc]['Unknown'] += 1
                    cnt['Unknown'] += 1
                    stypes.add('Unknown')

    cnt_loc['All'] = cnt


    
    # Create subplots: use 'domain' type for Pie subplot
    fig = make_subplots(rows=2, cols=4, specs=[[{'type':'domain'}] * 4, [{'type':'domain'}] * 4])
    annots = []
    st_colors = {}
    coords = {
        'Jazan': (0.08, 0.19),
        'Jeddah': (0.37, 0.19),
        'Alhasa': (0.63, 0.19),
        'Riyadh': (0.93, 0.19),
        'Madina': (0.07, 0.82),
        'Hail': (0.37, 0.82),
        'Makkah': (0.63, 0.82),
        'All': (0.91, 0.82)}
    
    for i, loc in enumerate(cnt_loc.keys()):
        cnt = dict(cnt_loc[loc].most_common(7))
        
        x = i // 4 + 1
        y = i % 4 + 1
        labels = ['ST-' + x for x in list(cnt.keys())]
        clrs = []
        for l in labels:
            if l in st_colors:
                clrs.append(st_colors[l])
            else:
                st_colors[l] = colors[len(st_colors)]
                clrs.append(st_colors[l])
        fig.add_trace(
            go.Pie(labels=labels,
                   values=list(cnt.values()),
                   name=loc,
                   marker=dict(colors=clrs)),
            x, y)
        annots.append(dict(
            text=loc, x=coords[loc][0], y=coords[loc][1], font_size=10, showarrow=False))
    print(coords)
    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(
        title_text="Sequence types by region",
        # Add annotations in the center of the donut pies.
        annotations=annots)
    fig.write_image('types.png')

if __name__ == '__main__':
    main()
