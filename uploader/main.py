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
    with gzip.open(sequence_read1, 'rt') as f:
        for record in SeqIO.parse(f, 'fastq'):
            pass
    return true


@ck.command()
@ck.option('--uploader-project', default='cborg-j7d0g-y651nepk74ziw3p', help='MRSA FASTQ sequences project uuid')
@ck.option('--sequence-read1', '-sr1', help='Gzipped FASTQ File (*.fastq.gz) read 1')
@ck.option('--sequence-read2', '-sr2', help='Gzipped FASTQ File (*.fastq.gz) read 2')
@ck.option('--metadata-file', '-m', help='METADATA File')
def main(uploader_project, sequence_read1, sequence_read2, metadata_file):
    validate_fastq(sequence_read1)
    validate_fastq(sequence_read2)
    metadata = yaml.load(metadata_file, Loader=yaml.FullLoader)
    
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
        "sequence_label": metadata['label'],
        "upload_app": "mrsa_uploader",
        "upload_ip": external_ip,
        "upload_user": "%s@%s" % (username, socket.gethostname())
    }

    col.save_new(owner_uuid=uploader_project, name="%s uploaded by %s from %s" %
                 (seqlabel, properties['upload_user'], properties['upload_ip']),
                 properties=properties, ensure_unique_name=True)

    print(json.dumps(col.api_response()))


if __name__ == '__main__':
    main()
