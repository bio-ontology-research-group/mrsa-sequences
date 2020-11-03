#!/usr/bin/env python
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
from analyzer.report import generate_report


logging.basicConfig(format="[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO)
logging.getLogger("googleapiclient.discovery").setLevel(logging.WARN)

ARVADOS_API_HOST = os.environ.get('ARVADOS_API_HOST', 'cborg.cbrc.kaust.edu.sa')
ARVADOS_API_TOKEN = os.environ.get('ARVADOS_API_TOKEN', '')

def run_workflow(api, parent_project, workflow_uuid, name, inputobj):
    project = api.groups().create(body={
        "group_class": "project",
        "name": name,
        "owner_uuid": parent_project,
    }, ensure_unique_name=True).execute()

    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(json.dumps(inputobj, indent=2).encode('utf-8'))
        tmp.flush()
        cmd = ["arvados-cwl-runner",
               "--submit",
               "--no-wait",
               "--project-uuid=%s" % project["uuid"],
               "arvwf:%s" % workflow_uuid,
               tmp.name]
        logging.info("Running %s" % ' '.join(cmd))
        proc = subprocess.run(cmd, capture_output=True)
    return project, proc

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


def submit_new_request(
        api, workflows_project, metagenome_workflow_uuid, sample_id,
        portable_data_hash):
    inputobj = {
        "kraken_db": {
            "class": "Directory",
            "location": "keep:da380d473187b77b9248dd8939dd8719+5443/minikraken"
        },
        "snippy_ref": {
            "class": "File",
            "location": "keep:93b026cb22456ff8bc55a47b736d439a+69/reference.fasta"
        },
        "sample_id": sample_id
    }
    inputobj["fastq1"] = {
        "class": "File",
        "location": "keep:%s/reads1.fastq.gz" % portable_data_hash
    }
    inputobj["fastq2"] = {
        "class": "File",
        "location": "keep:%s/reads2.fastq.gz" % portable_data_hash
    }
    name = f'Metagenome analysis for {sample_id}'
    project, proc = run_workflow(
        api, workflows_project, metagenome_workflow_uuid, name, inputobj)
    status = 'error'
    container_request = None
    if proc.returncode != 0:
        logging.error(proc.stderr.decode('utf-8'))
    else:
        output = proc.stderr.decode('utf-8')
        lines = output.splitlines()
        if lines[-2].find('container_request') != -1:
            container_request = lines[-2].split()[-1]
            status = 'submitted'
    return container_request, status


def submit_pangenome(
        api, workflows_project, pangenome_workflow_uuid, data):
    inputobj = {
        "gff_files": [],
        "reference": {
            "class": "File",
            "location": "keep:1630555a9f4d1d70d5bc19ac5f1d6800+133/reference.fasta"
        },
        "reference_gb": {
            "class": "File",
            "location": "keep:1630555a9f4d1d70d5bc19ac5f1d6800+133/reference.gb"
        },
        "metadata": {
            "class": "File",
            "location": "keep:e5c2e53119ea3aa1d0a2fd44de1d1a69+60/metadata.tsv"
        },
        "dirs": [],
    }
    for s_id, pdh in data:
        inputobj["gff_files"].append({
            "class": "File",
            "location": f'keep:{pdh}/{s_id}.gff'})
        inputobj["dirs"].append({
            "class": "Directory",
            "location": f'keep:{pdh}/{s_id}'})
    
    name = f'Pangenome analysis for'
    project, proc = run_workflow(
        api, workflows_project, pangenome_workflow_uuid, name, inputobj)
    status = 'error'
    container_request = None
    if proc.returncode != 0:
        logging.error(proc.stderr.decode('utf-8'))
    else:
        output = proc.stderr.decode('utf-8')
        lines = output.splitlines()
        if lines[-2].find('container_request') != -1:
            container_request = lines[-2].split()[-1]
            status = 'submitted'
    return container_request, status


    
@ck.command()
@ck.option('--fastq-project', '-fp', default='cborg-j7d0g-y651nepk74ziw3p', help='MRSA FASTQ sequences project uuid')
@ck.option('--workflows-project', '-wp', default='cborg-j7d0g-lcux1tdrdshvul7', help='MRSA workflows project uuid')
@ck.option('--metagenome-workflow-uuid', '-mwid', default='cborg-7fd4e-3ig4fl4bz90uydt', help='Metagenome workflow uuid')
@ck.option('--pangenome-workflow-uuid', '-pwid', default='cborg-7fd4e-qhxoc5ddgrti3tq', help='Pangenome workflow uuid')
@ck.option('--pangenome-result-col-uuid', '-prcid', default='cborg-4zz18-5e3rl41vfzpqs9q', help='Pangenome workflow uuid')
def main(fastq_project, workflows_project, metagenome_workflow_uuid, pangenome_workflow_uuid, pangenome_result_col_uuid): 
    logging.info("Starting a analysis run")

    api = arvados.api('v1', host=ARVADOS_API_HOST, token=ARVADOS_API_TOKEN)
    col = arvados.collection.Collection(api_client=api)
    state = {}
    if os.path.exists('state.json'):
        state = json.loads(open('state.json').read())
    reads = arvados.util.list_all(api.collections().list, filters=[["owner_uuid", "=", fastq_project]])
    pangenome_data = []
    report_data = {'kraken': [], 'mlst': [], 'resistome': [], 'virulome': [], 'prokka': []}
    update_pangenome = False
    for it in reads[1:]:
        col = api.collections().get(uuid=it['uuid']).execute()
        if 'sequence_label' not in it['properties']:
            continue
        sample_id = it['properties']['sequence_label']
        if 'analysis_status' in it['properties']:
            pangenome_data.append((sample_id, col['portable_data_hash']))
            col_reader = CollectionReader(col['uuid'])
            report_data['kraken'].append((sample_id, get_kraken_report(col_reader)))
            report_data['mlst'].append((sample_id, get_mlst_report(col_reader)))
            report_data['resistome'].append((sample_id, get_resistome_report(col_reader)))
            report_data['virulome'].append((sample_id, get_virulome_report(col_reader)))
            report_data['prokka'].append((sample_id, get_prokka_report(col_reader)))
        continue
        if sample_id not in state:
            state[sample_id] = {
                'status': 'new',
                'container_request': None,
                'output_collection': None,
            }
        sample_state = state[sample_id]
        if sample_state['status'] == 'new':
            container_request, status = submit_new_request(
                api, workflows_project, metagenome_workflow_uuid, sample_id,
                it['portable_data_hash'])
            sample_state['status'] = status
            sample_state['container_request'] = container_request
            logging.info('Submitted analysis request for %s', sample_id)
        elif sample_state['status'] == 'submitted':
            # TODO: check container request status
            if sample_state['container_request'] is None:
                raise Exception("Container request cannot be empty when status is submitted")
            cr = api.container_requests().get(
                uuid=sample_state["container_request"]).execute()
            cr_state = get_cr_state(api, cr)
            logging.info('Container request for %s is %s', sample_id, cr_state)
            if cr_state == 'Complete':
                out_col = api.collections().get(uuid=cr["output_uuid"]).execute()
                sample_state['output_collection'] = cr["output_uuid"]
                sample_state['status'] = 'complete'
                # Copy output files to reads collection
                it['properties']['analysis_status'] = 'complete'
                api.collections().update(
                    uuid=it['uuid'],
                    body={"manifest_text": col["manifest_text"] + out_col["manifest_text"],
                          "properties": it["properties"]}).execute()
                pangenome_data.append((sample_id, col['portable_data_hash']))
                update_pangenome = True
            elif cr_state == 'Failed':
                state[sample_id] = {
                    'status': 'new',
                    'container_request': None,
                    'output_collection': None,
        
                }
        elif sample_state['status'] == 'complete':
            # TODO: do nothing
            pass
    if update_pangenome:
        container_request, status = submit_pangenome(api, workflows_project, pangenome_workflow_uuid, pangenome_data)
        if status == 'submitted':
            state['last_pangenome_request'] = container_request
            state['last_pangenome_request_status'] = 'submitted'
            logging.info('Submitted pangenome request %s', container_request)
    else:
        cr = api.container_requests().get(
            uuid=state["last_pangenome_request"]).execute()
        cr_state = get_cr_state(api, cr)
        logging.info('Container request for pangenome workflow is %s', cr_state)
        if state['last_pangenome_request_status'] == 'submitted' and cr_state == 'Complete':
            logging.info('Updating results collection')
            out_col = api.collections().get(uuid=cr["output_uuid"]).execute()
            api.collections().update(
                uuid=pangenome_result_col_uuid,
                body={"manifest_text": out_col["manifest_text"]}).execute()
            state['last_pangenome_request_status'] = 'complete'

    col_reader = CollectionReader(pangenome_result_col_uuid)
    report_data["iqtree"] = get_iqtree_result(col_reader)
    report_data["roary_svg"] = get_roary_svg(col_reader)
    report_data["roary_stats"] = get_roary_stats(col_reader)
    generate_report(report_data)
    
    with open('state.json', 'w') as f:
        f.write(json.dumps(state))

def get_roary_svg(col):
    with col.open('gene_presence_absence.svg') as f:
        return f.read().strip()

def get_roary_stats(col):
    with col.open('summary_statistics.txt') as f:
        result = []
        for line in f:
            it = line.strip().split('\t')
            result.append(it)
        return result


def get_iqtree_result(col):
    with col.open('core.full.aln.treefile', 'r') as f:
        return f.read().strip()

def get_kraken_report(col):
    result = []
    with col.open('kraken_report.txt', "r") as f:
        for line in f:
            it = line.strip().split('\t')
            if it[3] == 'S':
                result.append((float(it[0]), it[4], it[5].strip()))
                if len(result) == 4:
                    break
    return result

def get_mlst_report(col):
    result = []
    with col.open('mlst.tsv', "r") as f:
        line = next(f)
        it = line.strip().split('\t')
        result = it[1:]
    while len(result) < 9:
        result.append('-')
    return result

def get_resistome_report(col):
    result = set()
    with col.open('abricate_resfinder.tsv', "r") as f:
        next(f)
        for line in f:
            it = line.strip().split('\t')
            result |= set(it[-1].split(';'))
    # print()
    return result

def get_virulome_report(col):
    result = []
    with col.open('abricate_vfdb.tsv', "r") as f:
        next(f)
        for line in f:
            it = line.strip().split('\t')
            result.append((it[5], float(it[9])))
    return result

def get_prokka_report(col):
    result = {}
    with col.open('prokka/prokka.txt', "r") as f:
        next(f)
        for line in f:
            it = line.strip().split(': ')
            result[it[0]] = it[1]
    return result


if __name__ == '__main__':
    main()
