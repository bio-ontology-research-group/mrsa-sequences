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
        for line in lines:
            if line.find('container_request') != -1:
                container_request = line.split()[-1]
                status = 'submitted'
                break
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
        for line in lines:
            if line.find('container_request') != -1:
                container_request = line.split()[-1]
                status = 'submitted'
                break
    return container_request, status


@ck.command()
@ck.option('--fastq-project', '-fp', default='cborg-j7d0g-1reggns1q6sti0i', help='MRSA FASTQ sequences project uuid')
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
        'ID00840', 'ID00841', 'ID00842', 'ID00843', 'ID00844',
        'bad_samples'])

    core_bad_samples = set([
        'ID00099', 'ID00100', 'ID00117', 'ID00118', 'ID00314',
        'ID00597', 'ID00088', 'ID00297', 'ID00610', 'ID00740',
        'ID00788', 'ID00231'
    ])
    bad_samples |= core_bad_samples
    # # Environmental samples
    # for i in range(464, 523):
    #     bad_samples.add(f'MRSA{i}')
    # # Environmental samples p.hong
    # for i in range(51, 57):
    #     bad_samples.add(f'MRSA{i:03d}')
    # # Environmental samples p.hong
    # for i in range(560, 845):
    #     bad_samples.add(f'MRSA{i}')
    # missing = set()
    # for i in range(523, 560):
    #     missing.add('ID00' + str(i))
    try:
        for it in reads[1:]:
            col = api.collections().get(uuid=it['uuid']).execute()
            if 'sequence_label' not in it['properties']:
                continue

            sample_id = it['properties']['sequence_label']

            # if sample_id not in missing:
            #     continue
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
                # report_data['kraken'].append((sample_id, get_kraken_report(col_reader)))
                # report_data['mlst'].append((sample_id, get_mlst_report(col_reader)))
                # report_data['resistome'].append((sample_id, get_resistome_report(col_reader)))
                # report_data['virulome'].append((sample_id, get_virulome_report(col_reader)))
                # report_data['prokka'].append((sample_id, get_prokka_report(col_reader, sample_id)))
                if sample_id not in bad_samples:
                    # pangenome_data.append((sample_id, out_col['portable_data_hash']))
                    # print('Saving files for', sample_id)
                    save_files(sample_id, col_reader)
                    cr = api.container_requests().get(
                        uuid=sample_state["container_request"]).execute()
                    # get_snippy_output(cr)
                    continue
            elif sample_state['status'] == 'new':
                if proc_cnt == 10: # Do not submit more than 10 jobs
                    continue
                if sample_id in bad_samples:
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
        if update_pangenome:
            container_request, status = submit_pangenome(api, workflows_project, pangenome_workflow_uuid, pangenome_data)
            if status == 'submitted':
                state['last_pangenome_request'] = container_request
                state['last_pangenome_request_status'] = 'submitted'
                print('Submitted pangenome request', container_request)
        elif "last_pangenome_request" in state:
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

        # col_reader = CollectionReader(pangenome_result_col_uuid, num_retries=5)
        # report_data["iqtree"] = get_iqtree_result(col_reader)
        # report_data["roary_svg"] = get_roary_svg(col_reader)
        # report_data["roary_stats"] = get_roary_stats(col_reader)
        # snp_dists, hist_data = get_snp_dists(col_reader)
        # report_data["snp_dists"] = snp_dists
        # report_data["snp_hist"] = {'nums': json.dumps(hist_data), 'start': 0, 'end': max(hist_data)}
        # report_data["core"] = get_core_genome(col_reader)
        
        # del report_data["roary_svg"]
        # del report_data["snp_dists"]
        with open('data/analysis.json', 'w') as f:
            f.write(json.dumps(report_data))
        # generate_report(report_data)
        
    except Exception as e:
        print(sample_state)
        traceback.print_exc()

    with open('state.json', 'w') as f:
        f.write(json.dumps(state))

def save_file(col, src, dst):
    try:
        with col.open(src, 'rb') as f:
            with open(dst, "wb") as w:
                content = f.read(128*1024)
                while content:
                    w.write(content)
                    content = f.read(128*1024)
    except Exception as e:
        print(e)
        print(col, src)

def save_files(sample_id, col):
    # Save skesa congigs
    save_file(col, 'skesa_contigs.fa', f'data/contigs/{sample_id}.fa')

    # Save snippy output
    snippy_root = f'data/snippy/{sample_id}/'
    if not os.path.exists(snippy_root):
        os.makedirs(snippy_root)
    filename = 'snps.vcf'
    filename_aligned = 'snps.aligned.fa'
    filename_txt = 'snps.txt'
        
    save_file(col, filename, snippy_root + 'snps.vcf')
    save_file(col, filename_aligned, snippy_root + 'snps.aligned.fa')
    save_file(col, filename_txt, snippy_root + 'snps.txt')

    # Save prokka output
    prokka_root = f'data/prokka/'
    filename = f'{sample_id}.gff'
    save_file(col, filename, prokka_root + f'{sample_id}.gff')

    # Save ResFinder
    resfinder_root = 'data/resfinder/'
    filename = 'abricate_resfinder.tsv'
    save_file(col, filename, resfinder_root + f'{sample_id}.tsv')

    # Save MLST
    mlst_root = 'data/mlst/'
    filename = 'mlst.tsv'
    save_file(col, filename, mlst_root + f'{sample_id}.tsv')

    # Save Kraken
    kraken_root = 'data/kraken/'
    filename = 'kraken_report.txt'
    save_file(col, filename, kraken_root + f'{sample_id}.tsv')
    


# def get_snippy_output(container_request):
    

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
    while len(result) < 4:
        result.append((0.0, '-', '-'))
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
