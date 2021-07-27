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

sys.path.insert(0, '')


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
               "--debug",
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
            "location": "keep:963fa93ead9e477fddfe707a59a4f329+204/reference.fasta"
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
        "gff_files": [
            {
                "class": "File",
                "location": "keep:963fa93ead9e477fddfe707a59a4f329+204/Reference.gff"
            },
        ],
        "reference": {
            "class": "File",
            "location": "keep:963fa93ead9e477fddfe707a59a4f329+204/reference.fasta"
        },
        "reference_gb": {
            "class": "File",
            "location": "keep:963fa93ead9e477fddfe707a59a4f329+204/reference.gb"
        },
        "metadata": {
            "class": "File",
            "location": "keep:e5c2e53119ea3aa1d0a2fd44de1d1a69+60/metadata.tsv"
        },
        "dirs": [],
    }
    for s_id, pdh in data:
        s_id = s_id.replace('ID00', 'MRSA')
        inputobj["gff_files"].append({
            "class": "File",
            "location": f'keep:{pdh}/prokka/{s_id}.gff'})
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
@ck.option('--fastq-result-project', '-frp', default='cborg-j7d0g-3udc153j2uo6bs2', help='MRSA FASTQ sequences project uuid')
def main(fastq_project, workflows_project, metagenome_workflow_uuid,
         pangenome_workflow_uuid, pangenome_result_col_uuid, fastq_result_project): 
    logging.info("Starting a analysis run")

    api = arvados.api('v1', host=ARVADOS_API_HOST, token=ARVADOS_API_TOKEN)
    col = arvados.collection.Collection(api_client=api, num_retries=5)
    state = {}
    if os.path.exists('state.json'):
        state = json.loads(open('state.json').read())
    reads = arvados.util.list_all(api.collections().list, filters=[["owner_uuid", "=", fastq_project]])
    pangenome_data = []
    report_data = {'kraken': [], 'mlst': [], 'resistome': [], 'virulome': [], 'prokka': []}
    update_pangenome = False
    proc_cnt = 0
    bad_samples = set([
        'MRSA095', 'MRSA096', 'MRSA097', 'MRSA098', 'MRSA099', 'MRSA100',
        'MRSA101', 'MRSA102', 'MRSA117', 'MRSA118', 'MRSA124', 'MRSA133',
        'MRSA187', 'MRSA261', 'MRSA314', 'MRSA355', 'MRSA357', 'MRSA360',
        'MRSA361', 'MRSA390', 'MRSA420', 'MRSA422', 'MRSA477',
        'MRSA028', 'MRSA070', 'MRSA116', 'MRSA179', 'MRSA243', 'MRSA270',
        'MRSA372', 'MRSA384', 'MRSA413', 'MRSA442', 'MRSA478', 'MRSA480',
        'MRSA481', 'MRSA490', 'MRSA491', 'MRSA500', 'MRSA501', 'MRSA502', 'MRSA503',
        'MRSA088', 'MRSA112', 'MRSA260', 'ID00277', 'ID00274', 'ID00253', 'ID00244',
        'ID00243', 'ID00224', 'ID00208', 
    ])
    # Environmental samples
    for i in range(464, 523):
        bad_samples.add(f'MRSA{i}')

    # Snippy core problem
    for i in range(241, 282):
        bad_samples.add(f'ID00{i}')

    try:
        for it in reads[1:]:
            col = api.collections().get(uuid=it['uuid']).execute()
            if 'sequence_label' not in it['properties']:
                continue

            sample_id = it['properties']['sequence_label']
            if sample_id not in state:
                state[sample_id] = {
                    'status': 'new',
                    'container_request': None,
                    'output_collection': None,
                }
            sample_state = state[sample_id]
            if sample_state['status'] == 'complete':
                out_col = api.collections().get(
                    uuid=sample_state['output_collection']).execute()
                col_reader = CollectionReader(out_col['uuid'], num_retries=5)
                report_data['kraken'].append((sample_id, get_kraken_report(col_reader)))
                report_data['mlst'].append((sample_id, get_mlst_report(col_reader)))
                report_data['resistome'].append((sample_id, get_resistome_report(col_reader)))
                report_data['virulome'].append((sample_id, get_virulome_report(col_reader)))
                report_data['prokka'].append((sample_id, get_prokka_report(col_reader, sample_id)))
                if sample_id not in bad_samples:

                    pangenome_data.append((sample_id, out_col['portable_data_hash']))
                    #print('Saving contigs for', sample_id)
                    #save_contigs(sample_id, col_reader)
                    # continue
            
            if sample_state['status'] == 'new':
                if proc_cnt == 1: # Do not submit more than 10 jobs
                    continue
                container_request, status = submit_new_request(
                    api, workflows_project, metagenome_workflow_uuid, sample_id,
                    it['portable_data_hash'])
                sample_state['status'] = status
                sample_state['container_request'] = container_request
                print(f'Submitted analysis request for {sample_id}')
                proc_cnt += 1
            elif sample_state['status'] == 'submitted':
                # TODO: check container request status
                if sample_state['container_request'] is None:
                    raise Exception("Container request cannot be empty when status is submitted")
                try:
                    cr = api.container_requests().get(
                        uuid=sample_state["container_request"]).execute()
                    cr_state = get_cr_state(api, cr)
                except Exception as e:
                    print(e)
                    cr_state = 'Failed'
                    print(f'Container request for {sample_id} is {cr_state}')
                if cr_state == 'Complete':
                    out_col = api.collections().get(uuid=cr["output_uuid"]).execute()
                    sample_state['output_collection'] = cr["output_uuid"]
                    sample_state['status'] = 'complete'
                    # Copy output files to reads collection
                    it['properties']['analysis_status'] = 'complete'
                    res = api.collections().update(
                        uuid=it['uuid'],
                        body={"properties": it["properties"]}).execute()
                    # update_pangenome = True
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
                print('Submitted pangenome request', container_request)
        else:
            cr = api.container_requests().get(
                uuid=state["last_pangenome_request"]).execute()
            cr_state = get_cr_state(api, cr)
            print(f'Container request for pangenome workflow is {cr_state}')
            if state['last_pangenome_request_status'] == 'submitted' and cr_state == 'Complete':
                print('Updating results collection')
                out_col = api.collections().get(uuid=cr["output_uuid"]).execute()
                api.collections().update(
                    uuid=pangenome_result_col_uuid,
                    body={"manifest_text": out_col["manifest_text"]}).execute()
                state['last_pangenome_request_status'] = 'complete'

        col_reader = CollectionReader(pangenome_result_col_uuid, num_retries=5)
        report_data["iqtree"] = get_iqtree_result(col_reader)
        report_data["roary_svg"] = get_roary_svg(col_reader)
        report_data["roary_stats"] = get_roary_stats(col_reader)
        snp_dists, hist_data = get_snp_dists(col_reader)
        report_data["snp_dists"] = snp_dists
        report_data["snp_hist"] = {'nums': json.dumps(hist_data), 'start': 0, 'end': max(hist_data)}
        report_data["core"] = get_core_genome(col_reader)
        
        del report_data["roary_svg"]
        del report_data["snp_dists"]
        with open('data/analysis.json', 'w') as f:
            f.write(json.dumps(report_data))
        #generate_report(report_data)
        
    except Exception as e:
        print(sample_state)
        traceback.print_exc()

    with open('state.json', 'w') as f:
        f.write(json.dumps(state))


def save_contigs(sample_id, col):
    sample_id = sample_id.replace('ID00', 'MRSA')
    with col.open('skesa_contigs.fa', 'rb') as f:
        with open(f'data/contigs/{sample_id}.fa', "wb") as w:
            content = f.read(128*1024)
            while content:
                w.write(content)
                content = f.read(128*1024)

def get_core_genome(col):
    result = []
    with col.open('core.txt') as f:
        next(f)
        for line in f:
            it = list(line.strip().split('\t'))
            it.append(round(float(it[2]) / float(it[1]) * 100, 2))
            result.append(it)
    return result

def get_snp_dists(col):
    result = {'body': []}
    hist_data = []
    with col.open('core.full.tab') as f:
        result['header'] = next(f).strip().split('\t')
        for line in f:
            it = line.strip().split('\t')
            result['body'].append(it)
            hist_data += list(map(int, it[1:]))
    return result, hist_data
    
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
    return list(result)

def get_virulome_report(col):
    result = []
    with col.open('abricate_vfdb.tsv', "r") as f:
        next(f)
        for line in f:
            it = line.strip().split('\t')
            result.append((it[5], float(it[9])))
    return result

def get_prokka_report(col, sample_id):
    sample_id = sample_id.replace('ID00', 'MRSA')
    result = {'organism': '', 'contigs': '0', 'bases': '0', 'CDS': '0', 'rRNA': '0', 'tRNA': '0', 'tmRNA':'0'}
    filename = 'prokka/prokka.txt'
    try:
        f = col.open(filename, 'r')
        f.close()
    except Exception as e:
        filename = f'prokka/{sample_id}.txt'
    try:
        with col.open(filename, "r") as f:
            next(f)
            for line in f:
                it = line.strip().split(': ')
                result[it[0]] = it[1]
    except Exception as e:
        print(e)
    
    return result


if __name__ == '__main__':
    main()
