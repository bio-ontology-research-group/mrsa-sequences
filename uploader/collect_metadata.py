import click as ck
import yaml
import os
import csv

@ck.command()
def main():
    drug_names = {}
    ints = {}
    with open('uploader/options.yml') as f:
        options = yaml.load(f, Loader=yaml.FullLoader)
        drugs_list = options['antimicrobial_agent']
        for key, value in drugs_list.items():
            drug_names[value] = key
        ints_list = options['interpretation']
        for key, value in ints_list.items():
            ints[value] = key

    drug_uris, drugs = drug_names.keys(), drug_names.values()
    print(drug_uris, drugs)
    drugs = list(drugs)
    drugs.remove('Mupirocin')
    files = os.listdir('data/metadata/')
    files = sorted(files)
    with open('data/traits.tsv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['UID'] + list(drugs))
        for fname in files:
            with open('data/metadata/' + fname) as f:
                sample_id, _ = os.path.splitext(fname)
                doc = yaml.load(f, Loader=yaml.FullLoader)
                mics = doc['phenotypes']['susceptibility']
                data = {}
                for item in mics:
                    data[drug_names[item['antimicrobial_agent']]] = '1' if ints[item['interpretation']] == 'R' else '0' #  + ':' + item['mic']
                row = [sample_id]
                for d in drugs:
                    if d in data:
                        row.append(data[d])
                    else:
                        row.append('0')
                if len(data):
                    writer.writerow(row)


if __name__ == '__main__':
    main()
