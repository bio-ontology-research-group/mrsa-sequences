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


ARVADOS_API_HOST = os.environ.get('ARVADOS_API_HOST', 'cborg.cbrc.kaust.edu.sa')
ARVADOS_API_TOKEN = os.environ.get('ARVADOS_API_TOKEN', '')

def upload_file(col, filename_local, filename_remote):
    lf = open(filename_local, 'rb')
    with col.open(filename_remote, "wb") as f:
        r = lf.read(65536)
        while r:
            f.write(r)
            r = lf.read(65536)
    lf.close()

def validate_fastq(fastq_file):
    with gzip.open(fastq_file, 'rt') as f:
        for record in SeqIO.parse(f, 'fastq'):
            pass
    return True


@ck.command()
@ck.option('--fastq-project', '-fp', default='cborg-j7d0g-y651nepk74ziw3p', help='MRSA FASTQ sequences project uuid')
@ck.option('--metagenome-workflow-uuid', '-mwid', default='', help='Metagenome workflow uuid')
@ck.option('--pangenome-workflow-uuid', '-pwid', default='', help='Pangenome workflow uuid')
def main(fastq_project, metagenome_workflow_uuid, pangenome_workflow_uuid):
    metadata = yaml.load(open(metadata_file), Loader=yaml.FullLoader)
    validate_fastq(sequence_read1)
    validate_fastq(sequence_read2)
    
    api = arvados.api('v1', host=ARVADOS_API_HOST, token=ARVADOS_API_TOKEN)
    col = arvados.collection.Collection(api_client=api)

    upload_file(col, sequence_read1, 'reads1.fastq.gz')
    upload_file(col, sequence_read2, 'reads2.fastq.gz')
    upload_file(col, metadata_file, 'metadata.yaml')
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

    try:
        username = getpass.getuser()
    except KeyError:
        username = "unknown"

    properties = {
        "sequence_label": metadata['sample'],
        "upload_app": "mrsa_uploader",
        "upload_ip": external_ip,
        "upload_user": "%s@%s" % (username, socket.gethostname())
    }

    col.save_new(owner_uuid=uploader_project, name="%s uploaded by %s from %s" %
                 (metadata['sample'], properties['upload_user'], properties['upload_ip']),
                 properties=properties, ensure_unique_name=True)

    print(json.dumps(col.api_response()))


if __name__ == '__main__':
    main()
