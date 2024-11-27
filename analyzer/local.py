#!/usr/bin/env python
import sys
import click as ck
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
from multiprocessing.pool import ThreadPool

sys.path.insert(0, '')


from analyzer.report import generate_report


logging.basicConfig(format="[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO)
logging.getLogger("googleapiclient.discovery").setLevel(logging.WARN)


def run_workflow(filepath, inputobj, cwd=None):
    
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(json.dumps(inputobj, indent=2).encode('utf-8'))
        tmp.flush()
        cmd = ["cwltool",
               filepath,
               tmp.name]
        logging.info("Running %s" % ' '.join(cmd))
        proc = subprocess.run(cmd, cwd=cwd)

    return proc


def submit_new_request(sample_id):
    inputobj = {
        "kraken_db": {
            "class": "Directory",
            "path": "/home/kulmanm/data/dbs/minikraken"
        },
        "snippy_ref": {
            "class": "File",
            "path": "/home/kulmanm/data/dbs/NC_007795.1.fasta"
        },
        "sample_id": sample_id,
        "fastq1":{
            "class": "File",
            "path": f"/home/kulmanm/data/mrsa/reads/{sample_id}_R1.fastq.gz"
        },
        "fastq2": {
            "class": "File",
            "path": f"/home/kulmanm/data/mrsa/reads/{sample_id}_R2.fastq.gz"
        }
    }
    name = f'Metagenome analysis for {sample_id}'
    metagenome_wf_path = '/home/kulmanm/KAUST/CBRC/mrsa-sequences/workflows/metagenome/mrsa-metagenome.cwl'
    cwd = f'/home/kulmanm/data/mrsa_analysis/{sample_id}'
    os.makedirs(cwd, exist_ok=True)
    project, proc = run_workflow(metagenome_wf_path, inputobj, cwd=cwd)
    status = 'error'
    if proc.returncode != 0:
        logging.error(proc.stderr.decode('utf-8'))
    else:
        status = 'success'
    return status


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
def main(): 
    logging.info("Starting a analysis run")
    
    reads = os.listdir('/home/kulmanm/data/mrsa/reads/')
    reads = [x.split('_')[0] for x in reads]
    reads = list(set(reads))

    tp = ThreadPool(20)
    
    for sample_id in reads:
        tp.apply_async(submit_new_request, (sample_id,))

    tp.close()
    tp.join()
    


def save_contigs(sample_id, col):
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
    return result

def get_virulome_report(col):
    result = []
    with col.open('abricate_vfdb.tsv', "r") as f:
        next(f)
        for line in f:
            it = line.strip().split('\t')
            result.append((it[5], float(it[9])))
    return result

def get_prokka_report(col, sample_id):
    result = {}
    filename = 'prokka/prokka.txt'
    try:
        f = col.open(filename, 'r')
        f.close()
    except Exception as e:
        filename = f'prokka/{sample_id}.txt'
    with col.open(filename, "r") as f:
        next(f)
        for line in f:
            it = line.strip().split(': ')
            result[it[0]] = it[1]
    return result


if __name__ == '__main__':
    main()
