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
from itertools import zip_longest

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
    report_data = {'kraken': [], 'mlst': [], 'resistome': []}
    update_pangenome = True
    proc_cnt = 0
    bad_samples = set([
        'ID00028', 'ID00070', 'ID00095', 'ID00096', 'ID00097',
        'ID00098', 'ID00101', 'ID00102', 'ID00116', 'ID00124',
        'ID00133', 'ID00179', 'ID00187', 'ID00212', 'ID00213',
        'ID00222', 'ID00243', 'ID00260', 'ID00261', 'ID00270',
        'ID00323', 'ID00349', 'ID00355', 'ID00356', 'ID00357',
        'ID00360', 'ID00361', 'ID00372', 'ID00384', 'ID00390',
        'ID00413', 'ID00420', 'ID00422', 'ID00423', 'ID00442',
        'ID00477', 'ID00478', 'ID00480', 'ID00481', 'ID00490',
        'ID00491', 'ID00499', 'ID00500', 'ID00501', 'ID00502',
        'ID00503', 'ID00514', 'ID00515', 'ID00517', 'ID00518',
        'ID00563', 'ID00568', 'ID00569', 'ID00574', 'ID00579',
        'ID00581', 'ID00582', 'ID00585', 'ID00589', 'ID00590',
        'ID00592', 'ID00600', 'ID00601', 'ID00602', 'ID00604',
        'ID00605', 'ID00607', 'ID00608', 'ID00609', 'ID00619',
        'ID00624', 'ID00629', 'ID00635', 'ID00643', 'ID00645',
        'ID00660', 'ID00661', 'ID00662', 'ID00667', 'ID00668',
        'ID00671', 'ID00672', 'ID00673', 'ID00687', 'ID00692',
        'ID00693', 'ID00717', 'ID00730', 'ID00736', 'ID00741',
        'ID00745', 'ID00747', 'ID00755', 'ID00758', 'ID00760',
        'ID00763', 'ID00773', 'ID00775', 'ID00776', 'ID00778',
        'ID00780', 'ID00812', 'ID00813', 'ID00814', 'ID00815',
        'ID00818', 'ID00820', 'ID00822', 'ID00825', 'ID00826',
        'ID00827', 'ID00829', 'ID00830', 'ID00837', 'ID00838',
        'ID00840', 'ID00841', 'ID00842', 'ID00843', 'ID00844',])

    core_bad_samples = set([
        'ID00099', 'ID00100', 'ID00117', 'ID00118', 'ID00314',
        'ID00597', 'ID00088', 'ID00297', 'ID00610', 'ID00740',
        'ID00788', 'ID00231'
    ])
    bad_samples |= core_bad_samples

    # print(' '.join(bad_samples))
    # return
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
        loc_names = {}
        for key, value in options['sample_collection_location'].items():
            loc_names[value] = key
        
    try:
        all_drugs = set()
        fp = 0
        tp = 0
        genotype = {'samples': [], 'location':[]}
        labs_resist = []
        labs_sensitive = []
        samples = []
        locations = []
        reads = os.listdir('data/resfinder')
        for it in reads:
            sample_id = os.path.splitext(it)[0]
            with open(f'data/metadata/{sample_id}.yaml') as f:
                metadata = yaml.load(f, Loader=yaml.FullLoader)
                location_id = metadata['sample']['collection_location']
                print(sample_id)
                report_data['kraken'].append((sample_id, get_kraken_report(sample_id)))
                report_data['mlst'].append((sample_id, get_mlst_report(sample_id)))
                report_data['resistome'].append((sample_id, get_resistome_report(sample_id)))
                location = loc_names[location_id]
                res_drugs = get_resistome_report(sample_id)
                header = res_drugs[0]
                for item in header:
                    if item not in genotype:
                        genotype[item] = []
                for item in res_drugs[1:]:
                    genotype['samples'].append(sample_id)
                    genotype['location'].append(location)
                    for col, value in zip_longest(header, item):
                        genotype[col].append(value)

                    # drug_ids = set([drug_names[drugs[x]] for x in res_drugs])
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
                locations.append(location)
        df = pd.DataFrame({'samples': samples, 'resistance': labs_resist,
                           'sensitive': labs_sensitive, 'location': locations})
        df.to_pickle('data/lab_resistance.pkl')
        df.to_csv('data/lab_resistance.csv')
        df = pd.DataFrame(genotype)
        df.to_csv('data/gt_resistance.csv')
        df.to_pickle('data/gt_resistance.pkl')
        
        # print(all_drugs)
        # drugs = []
        # for d in all_drugs:
        #     drugs.append({d: 'http://purl.obolibrary.org/obo/CHEBI_18208'})
        # with open('data/drugs.yml', 'w') as w:
        #     yaml.dump({'drugs': drugs}, w)

        with open('data/analysis.json', 'w') as f:
            f.write(json.dumps(report_data))

    except Exception as e:
        print(sample_state)
        traceback.print_exc()

def get_resistome_report(sample_id):
    result = []
    with open(f'data/resfinder/{sample_id}.tsv', "r") as f:
        for line in f:
            it = line.strip().split('\t')
            result.append(it)
    # print()
    return result


def get_kraken_report(sample_id):
    result = []
    with open(f'data/kraken/{sample_id}.tsv', "r") as f:
        for line in f:
            it = line.strip().split('\t')
            if it[3] == 'S':
                result.append((float(it[0]), it[4], it[5].strip()))
                if len(result) == 4:
                    break
    while len(result) < 4:
        result.append((0.0, '-', '-'))
    return result

def get_mlst_report(sample_id):
    result = []
    with open(f'data/mlst/{sample_id}.tsv', "r") as f:
        line = next(f)
        it = line.strip().split('\t')
        result = it[1:]
    while len(result) < 9:
        result.append('-')
    return result

def get_virulome_report(sample_id):
    result = []
    with col.open('abricate_vfdb.tsv', "r") as f:
        next(f)
        for line in f:
            it = line.strip().split('\t')
            result.append((it[5], float(it[9])))
    return result

def get_prokka_report(sample_id):
    result = {'organism': '', 'contigs': '0', 'bases': '0', 'CDS': '0', 'rRNA': '0', 'tRNA': '0', 'tmRNA':'0'}
    with open(f'data/prokka/{sample_id}.tsv', "r") as f:
        next(f)
        for line in f:
            it = line.strip().split(': ')
            result[it[0]] = it[1]
    return result


if __name__ == '__main__':
    main()
