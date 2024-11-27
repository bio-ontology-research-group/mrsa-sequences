import yaml
import json
import click as ck
import os


@ck.command()
def main():
    drug_names = {}
    inters = {}
    with open('uploader/options.yml') as f:
        options = yaml.load(f, Loader=yaml.FullLoader)
        drugs_list = options['antimicrobial_agent']
        for key, value in drugs_list.items():
            drug_names[value] = key
        inter_list = options['interpretation']
        for key, value in inter_list.items():
            inters[value] = key

    counts = {}
    files = os.listdir('data/metadata')
    for filename in files:
        with open(f'data/metadata/{filename}') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            drugs = data['phenotypes']['susceptibility']
            for item in drugs:
                drug, inter = drug_names[item['antimicrobial_agent']], inters[item['interpretation']]
                if drug == 'Vancomycin' and inter == 'R':
                    print(filename)
                if drug not in counts:
                    counts[drug] = {'R':0, 'I': 0, 'S': 0}
                counts[drug][inter] += 1
    for drug, count in counts.items():
        print(drug, count['R'] / (count['R'] + count['S']))

if __name__ == '__main__':
    main()
