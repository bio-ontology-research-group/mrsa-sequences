#!/usr/bin/env python
import sys
import click as ck
import arvados
from arvados.collection import CollectionReader
import os
import gzip
from Bio import SeqIO
import urllib
import getpass
import json
import yaml
import socket
import subprocess
import tempfile
import logging
import traceback
import pandas as pd

sys.path.insert(0, '')

logging.basicConfig(format="[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO)
logging.getLogger("googleapiclient.discovery").setLevel(logging.WARN)

ARVADOS_API_HOST = os.environ.get('ARVADOS_API_HOST', 'cborg.cbrc.kaust.edu.sa')
ARVADOS_API_TOKEN = os.environ.get('ARVADOS_API_TOKEN', '')

def get_cr_state(api, cr):
    if cr['container_uuid'] is None:
        return cr['state']
    c = api.containers().get(uuid=cr['container_uuid']).execute()
    if cr['state'] == 'Final' and c['state'] != 'Complete':
        return 'Cancelled'
    elif c['state'] in ['Locked', 'Queued']:
        if c['priority'] == 0:
            return 'On hold'
        else:
            return 'Queued'
    elif c['state'] == 'Complete' and c['exit_code'] != 0:
        return 'Failed'
    elif c['state'] == 'Running':
        if c['runtime_status'].get('error', None):
            return 'Failing'
        elif c['runtime_status'].get('warning', None):
            return 'Warning'
    return c['state']


    
@ck.command()
@ck.option('--fastq-project', '-fp', default='cborg-j7d0g-y651nepk74ziw3p', help='MRSA FASTQ sequences project uuid')
def main(fastq_project): 
    api = arvados.api('v1', host=ARVADOS_API_HOST, token=ARVADOS_API_TOKEN)
    col = arvados.collection.Collection(api_client=api, num_retries=5)
    state = {}
    if os.path.exists('state.json'):
        state = json.loads(open('state.json').read())
    reads = arvados.util.list_all(api.collections().list, filters=[["owner_uuid", "=", fastq_project]])
    pangenome_data = []
    report_data = {'kraken': [], 'mlst': [], 'resistome': [], 'virulome': [], 'prokka': []}
    update_pangenome = True
    proc_cnt = 0
    bad_samples = set([
        'MRSA095', 'MRSA096', 'MRSA097', 'MRSA098', 'MRSA099', 'MRSA100',
        'MRSA101', 'MRSA102', 'MRSA117', 'MRSA118', 'MRSA124', 'MRSA133',
        'MRSA187', 'MRSA261', 'MRSA314', 'MRSA355', 'MRSA357', 'MRSA360',
        'MRSA361', 'MRSA390', 'MRSA420', 'MRSA422', 'MRSA477'
    ])

    drug_names = {}
    with open('data/drugs.yml') as f:
        drugs = yaml.load(f, Loader=yaml.FullLoader)
        drugs = drugs['drugs']
        for key, value in drugs.items():
            drug_names[value] = key

    with open('uploader/options.yml') as f:
        options = yaml.load(f, Loader=yaml.FullLoader)
        drugs_list = options['antimicrobial_agent']
        for key, value in drugs_list.items():
            drug_names[value] = key
            drugs[key] = value
        
    try:
        all_drugs = set()
        fp = 0
        tp = 0
        genotype = {'samples': []}
        labs_resist = []
        labs_sensitive = []
        samples = []
        
        for it in reads[1:]:
            col = api.collections().get(uuid=it['uuid']).execute()
            if 'sequence_label' not in it['properties']:
                continue
            sample_id = it['properties']['sequence_label']
            if sample_id not in state:
                continue
            sample_state = state[sample_id]
            if sample_state['status'] == 'complete':
                out_col = api.collections().get(
                    uuid=sample_state['output_collection']).execute()
                if sample_id not in bad_samples:
                    col_reader = CollectionReader(out_col['uuid'])
                    res_drugs = get_resistome_report(col_reader)
                    header = res_drugs[0]
                    for item in header:
                        if item not in genotype:
                            genotype[item] = []
                    for item in res_drugs[1:]:
                        genotype['samples'].append(sample_id)
                        for col, value in zip(header, item):
                            genotype[col].append(value)
                    
                    # drug_ids = set([drug_names[drugs[x]] for x in res_drugs])
                    with open(f'/opt/data-mrsa/metadata/{sample_id}.yaml') as f:
                        metadata = yaml.load(f, Loader=yaml.FullLoader)
                        if not 'susceptibility' in metadata['phenotypes']:
                            continue
                        sus = metadata['phenotypes']['susceptibility']
                        meta_drugs = []
                        sens_drugs = []
                        for item in sus:
                            if item['interpretation'] == 'http://purl.obolibrary.org/obo/PATO_0001178':
                                meta_drugs.append((drug_names[item['antimicrobial_agent']], item['mic']))
                            else:
                                sens_drugs.append((drug_names[item['antimicrobial_agent']], item['mic']))
                    samples.append(sample_id)
                    labs_resist.append(meta_drugs)
                    labs_sensitive.append(sens_drugs)
        df = pd.DataFrame({'samples': samples, 'resistance': labs_resist,
                           'sensitive': labs_sensitive})
        df.to_pickle('data/lab_resistance.pkl')
        df = pd.DataFrame(genotype)
        df.to_pickle('data/gt_resistance.pkl')
        
        # print(all_drugs)
        # drugs = []
        # for d in all_drugs:
        #     drugs.append({d: 'http://purl.obolibrary.org/obo/CHEBI_18208'})
        # with open('data/drugs.yml', 'w') as w:
        #     yaml.dump({'drugs': drugs}, w)
    except Exception as e:
        print(sample_state)
        traceback.print_exc()

def get_resistome_report(col):
    result = []
    with col.open('abricate_resfinder.tsv', "r") as f:
        for line in f:
            it = line.strip().split('\t')
            result.append(it)
    # print()
    return result


if __name__ == '__main__':
    main()
