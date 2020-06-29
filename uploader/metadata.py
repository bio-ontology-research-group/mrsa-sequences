#!/usr/bin/env python
import click as ck
import json
import yaml


@ck.command()
@ck.option('--tsv-file', '-tf', help='TSV file with all metadata')
def main(tsv_file):
    with open(tsv_file) as f:
        next(f)
        for line in f:
            it = line.strip().split('\t')
            sample = it[0]
            bacteria = it[1]
            date = it[2]
            country = it[3]
            data = {
                'sample': sample,
                'bacteria': bacteria,
                'date': date,
                'country': country
            }
            with open(f'/opt/data-mrsa/metadata/{sample}.json', 'w') as f:
                f.write(json.dumps(data))

if __name__ == '__main__':
    main()
