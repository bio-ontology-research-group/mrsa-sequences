#!/usr/bin/env python
import click as ck
import json
import yaml


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
            bacteria = it[1]
            date = it[2]
            country = it[3]
            metadata = min_metadata.copy()
            metadata['sample']['sample_id'] = sample
            metadata['sample']['collection_date'] = date
            with open(f'/opt/data-mrsa/metadata/{sample}.yaml', 'w') as f:
                yaml.dump(metadata, f)

  
if __name__ == '__main__':
    main()
