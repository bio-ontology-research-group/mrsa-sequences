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
import pkg_resources
import schema_salad.schema
import schema_salad.ref_resolver
import schema_salad.jsonld_context
import traceback
from rdflib import Graph, Namespace
from pyshex.evaluate import evaluate
import logging


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

def validate_metadata(metadata_file):
    schema_resource = pkg_resources.resource_stream(__name__, "schema.yml")
    cache = {
        "https://raw.githubusercontent.com/bio-ontology-research-group/mrsa-sequences/master/uploader/schema.yml": schema_resource.read().decode("utf-8")}
    (document_loader,
     avsc_names,
     schema_metadata,
     metaschema_loader) = schema_salad.schema.load_schema(
         "https://raw.githubusercontent.com/bio-ontology-research-group/mrsa-sequences/master/uploader/schema.yml",
         cache=cache)

    shex = pkg_resources.resource_stream(
        __name__, "shex.rdf").read().decode("utf-8")

    if not isinstance(avsc_names, schema_salad.avro.schema.Names):
        print(avsc_names)
        return False

    try:
        doc, metadata = schema_salad.schema.load_and_validate(
            document_loader, avsc_names, metadata_file, True)
        g = schema_salad.jsonld_context.makerdf("workflow", doc, document_loader.ctx)
        rslt, reason = evaluate(
            g, shex, doc["id"],
            "https://raw.githubusercontent.com/bio-ontology-research-group/mrsa-sequences/master/uploader/shex.rdf#submissionShape")

        if not rslt:
            print(reason)

        return rslt
    except Exception as e:
        traceback.print_exc()
        logging.warn(e)
    return False

@ck.command()
@ck.option(
    '--uploader-project', default='cborg-j7d0g-1reggns1q6sti0i',
    help='MRSA FASTQ sequences project uuid')
@ck.option('--sequence-read1', '-sr1', help='Gzipped FASTQ File (*.fastq.gz) read 1')
@ck.option('--sequence-read2', '-sr2', help='Gzipped FASTQ File (*.fastq.gz) read 2')
@ck.option('--metadata-file', '-m', help='METADATA File')
def main(uploader_project, sequence_read1, sequence_read2, metadata_file):
    if not validate_metadata(metadata_file):
        return
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
        "sequence_label": metadata['sample']['sample_id'],
        "upload_app": "mrsa_uploader",
        "upload_ip": external_ip,
        "upload_user": "%s@%s" % (username, socket.gethostname())
    }

    col.save_new(owner_uuid=uploader_project, name="%s uploaded by %s from %s" %
                 (metadata['sample']['sample_id'], properties['upload_user'], properties['upload_ip']),
                 properties=properties, ensure_unique_name=True)

    print(json.dumps(col.api_response()))


if __name__ == '__main__':
    main()
