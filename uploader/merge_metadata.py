import re
import schema_salad.schema
import schema_salad.jsonld_context
import json
import sys
import os
import logging
import click as ck
import pkg_resources

@ck.command()
def main():
    schema_resource = pkg_resources.resource_stream(__name__, "schema.yml")
    cache = {
        "https://raw.githubusercontent.com/bio-ontology-research-group/mrsa-sequences/master/uploader/schema.yml": schema_resource.read().decode("utf-8")}
    (document_loader,
     avsc_names,
     schema_metadata,
     metaschema_loader) = schema_salad.schema.load_schema(
         "https://raw.githubusercontent.com/bio-ontology-research-group/mrsa-sequences/master/uploader/schema.yml",
         cache=cache)
    files = os.listdir('data/metadata')
    for filename in files:
        filepath = f'data/metadata/{filename}'
        id, ext = os.path.splitext(filename)
        doc_id = f"http://cbrc.kaust.edu.sa/mrsa-schema/{id}"
        doc, metadata = schema_salad.schema.load_and_validate(document_loader, avsc_names, filepath, False, False)
        doc['id'] = doc_id
        g = schema_salad.jsonld_context.makerdf(doc_id, doc, document_loader.ctx)
        print(g.serialize(format="ntriples"))



if __name__ == '__main__':
    main()
