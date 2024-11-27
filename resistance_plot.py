import plotly.graph_objects as go
import numpy as np
import pandas as pd
from analyzer.constants import SAMPLES
from collections import Counter

df = pd.read_pickle('data/lab_resistance.pkl')
df = df[df['samples'].isin(SAMPLES)]

print(df)
resist = Counter()
sens = Counter()
for row in df.itertuples():
    drugs = set([x for x, _ in row.resistance])
    for dr in drugs:
        resist[dr] += 1
    drugs = set([x for x, _ in row.sensitive])
    for dr in drugs:
        sens[dr] += 1
print(resist)
print(sens)
labels = set(resist.keys())
for d in sens.keys():
    if d not in labels:
        labels.add(d)
labels = list(labels)
labels_vals = []
for lab in labels:
    labels_vals.append(resist[lab])
labels = zip(labels, labels_vals)
labels = sorted(labels, key=lambda x: x[1], reverse=True)
labels = [x for x, _ in labels]
widths = np.array([10] * len(labels))
data = {
    "Sensitive": [],
    "Resistant": []
    
}
for d in labels:
    data['Resistant'].append(resist[d])
    data['Sensitive'].append(sens[d])
    

fig = go.Figure()
for key in data:
    fig.add_trace(go.Bar(
        name=key,
        y=data[key],
        x=np.cumsum(widths)-widths/2,
        width=widths,
    ))

fig.update_xaxes(
    tickvals=np.cumsum(widths)-widths/2,
    ticktext= ["%s" % (l,) for l, w in zip(labels, widths)]
)

fig.update_xaxes(range=[0,180])
fig.update_yaxes(range=[0,606])

fig.update_layout(
    title_text="Resitance/Sensitivity Chart",
    barmode="stack",
    uniformtext=dict(mode="hide", minsize=10),
)

fig.write_image('data/resistance.png')
