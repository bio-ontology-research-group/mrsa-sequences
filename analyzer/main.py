#!/usr/bin/env python
import click as ck
import arvados
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
        comp = subprocess.run(cmd, capture_output=True)
    if comp.returncode != 0:
        logging.error(comp.stderr.decode('utf-8'))

    return project

@ck.command()
@ck.option('--fastq-project', '-fp', default='cborg-j7d0g-y651nepk74ziw3p', help='MRSA FASTQ sequences project uuid')
@ck.option('--workflows-project', '-wp', default='cborg-j7d0g-lcux1tdrdshvul7', help='MRSA workflows project uuid')
@ck.option('--metagenome-workflow-uuid', '-mwid', default='cborg-7fd4e-3ig4fl4bz90uydt', help='Metagenome workflow uuid')
@ck.option('--pangenome-workflow-uuid', '-pwid', default='', help='Pangenome workflow uuid')
def main(fastq_project, workflows_project, metagenome_workflow_uuid, pangenome_workflow_uuid):    
    api = arvados.api('v1', host=ARVADOS_API_HOST, token=ARVADOS_API_TOKEN)
    col = arvados.collection.Collection(api_client=api)

    reads = arvados.util.list_all(api.collections().list, filters=[["owner_uuid", "=", fastq_project]])
    for r in reads[:1]:
        inputobj = {}
        inputobj["fastq1"] = {
            "class": "File",
            "location": "keep:%s/reads1.fastq.gz" % r["portable_data_hash"]
        }
        inputobj["fastq2"] = {
            "class": "File",
            "location": "keep:%s/reads2.fastq.gz" % r["portable_data_hash"]
        }
        inputobj["metadata"] = {
            "class": "File",
            "location": "keep:%s/metadata.yaml" % r["portable_data_hash"]
        }
        sample_id = r['properties']['sequence_label']
        name = f'Metagenome analysis for {sample_id}'
        run_workflow(api, workflows_project, metagenome_workflow_uuid, name, inputobj)

    

if __name__ == '__main__':
    main()
