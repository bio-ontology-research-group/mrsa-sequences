#!/usr/bin/env python
import click as ck
import json
import yaml
import csv
import os

@ck.command()
@ck.option('--tsv-file', '-tf', help='TSV file with all metadata')
def main(tsv_file):
    min_metadata = yaml.load(
        open('minimal_metadata_example.yaml'),
        Loader=yaml.FullLoader)
    with open(tsv_file) as f:
        next(f)
        for line in f:
            it = line.strip().split('\t')
            sample = it[0]
            sample_id = sample.replace('MRSA', 'ID0')
            phenotypes = load_phenotypes(sample_id)
            bacteria = it[1]
            date = it[2]
            country = it[3]
            metadata = min_metadata.copy()
            metadata['sample']['sample_id'] = sample
            metadata['sample']['collection_date'] = date
            metadata['phenotypes'] = phenotypes
            with open(f'/opt/data-mrsa/metadata/{sample}.yaml', 'w') as w:
                yaml.dump(metadata, w)

def load_phenotypes(sample_id):
    phenotypes = []
    filename = f'../data/vitek_csvs/{sample_id}-1.csv'
    if not os.path.exists(filename):
        return phenotypes
    with open(filename) as f:
        lines = f.read().splitlines()
    read = False
    for line in lines:
        if line.find('Antimicrobial') != -1:
            read = True
            continue
        if read:
            it = [x for x in line.split(',')[1:] if x and x != '«']
            if len(it) == 3 and it[0] not in ['NEG', 'POS']:
                d1 = it[0]
                mic = it[1]
                ip = it[2]
                phenotypes.append((d1, mic, ip))
            elif len(it) == 6:
                d1 = it[0]
                mic = it[1]
                ip = it[2]
                phenotypes.append((d1, mic, ip))
                d2 = it[3]
                mic = it[4]
                ip = it[5]
                phenotypes.append((d2, mic, ip))
            elif len(it) == 4:
                phenotypes.append((it[0], it[1], it[2]))
            elif len(it) == 5 and it[0] == 'Clindamycin':
                phenotypes.append((it[0], it[1], it[2]))
                phenotypes.append(('Trimethoprim/Sulfamethoxazole', it[3], it[4]))
            elif it[0] == 'NEG' or it[0] == 'POS':
                phenotypes.append(('Inducible Clindamycin Resistance', it[0], it[1]))
            else:
                if len(it) > 1:
                    print(sample_id, it)
    sus = []
    with open('options.yml') as f:
        options = yaml.load(f, Loader=yaml.FullLoader)
    drugs = options['antimicrobial_agent']
    inter = options['interpretation']
    for d, mic, ip in phenotypes:
        ip = ip.strip(' *')
        if d == 'Cefoxitin Screen':
            ip = 'R' if mic == 'POS' else 'S'
            d = 'Cefoxitin'
        if d in drugs:
            sus.append({
                'antimicrobial_agent': drugs[d],
                'mic': mic,
                'interpretation': inter[ip]
            })
        
    return {'susceptibility': sus}
  
if __name__ == '__main__':
    main()
