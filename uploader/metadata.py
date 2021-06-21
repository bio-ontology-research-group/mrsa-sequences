#!/usr/bin/env python
import click as ck
import json
import yaml
import csv
import os

@ck.command()
@ck.option('--tsv-file', '-tf', required=True, help='TSV file with all metadata')
def main(tsv_file):
    min_metadata = yaml.load(
        open('uploader/minimal_metadata_example.yaml'),
        Loader=yaml.FullLoader)
    options = yaml.load(open('uploader/options.yml'), Loader=yaml.FullLoader)
    with open(tsv_file) as f:
        for line in f:
            if not line.startswith('ID'):
                continue
            it = line.split('\t')
            sample = it[0]
            sample_id = sample.replace('MRSA', 'ID0')
            phenotypes = load_phenotypes(sample_id)
            bacteria = 'saureus'
            date = it[5].strip()
            country = format_location(options, 'Saudi Arabia')
            city = it[2].strip()
            provider = it[3].strip()
            hospital = it[4].strip()
            gender = it[7].strip()
            age = it[8].strip()
            specimen_source = it[9].strip()
            hospitalized = it[10].strip()
            metadata = min_metadata.copy()
            metadata['sample']['sample_id'] = sample
            metadata['sample']['collection_date'] = date
            metadata['sample']['collection_location'] = country
            if date:
                date = format_date(date)
                metadata['sample']['collection_date'] = date
            if city:
                city = format_location(options, city)
                metadata['sample']['collection_location'] = city
            if provider:
                metadata['sample']['collecting_institution'] = provider
            if specimen_source:
                specimen_source = format_source(options, specimen_source)
                metadata['sample']['specimen_source'] = [specimen_source,]
            if gender:
                gender = format_gender(options, gender)
                metadata['host']['host_sex'] = gender
            if age:
                age, unit = format_age(options, age)
                metadata['host']['host_age'] = age
                metadata['host']['host_age_unit'] = unit
            if hospitalized == 'hospitalized':
                hospitalized = format_hospitalized(options, hospitalized)
                metadata['host']['host_health_status'] = hospitalized
            if hospital:
                metadata['host']['host_hospital'] = hospital
            
            if phenotypes:
                metadata['phenotypes'] = phenotypes
            with open(f'data/metadata/{sample}.yaml', 'w') as w:
                yaml.dump(metadata, w)

def format_date(date):
    if date.find('.') != -1:
        it = date.split('.')
        d = it[0]
        m = it[1]
        y = it[2]
    elif date.find('/') != -1:
        it = date.split('/')
        d = it[1]
        m = it[0]
        y = it[2]
    else:
        return ''
    if len(y) == 2:
        y = '20' + y
    return f'{y}-{m}-{d}'

def format_location(options, city):
    ls = options['sample_collection_location']
    return ls[city]

def format_source(options, source):
    source = source.strip().lower()
    if source == 'tissue' or 'tissue sterile':
        source = 'tissue sample'
    elif source == 'blood':
        source = 'blood sample'
    
    ls = options['specimen_source']
    return ls[source.lower()]

def format_gender(options, gender):
    gs = options['host_sex']
    if gender == 'M' or 'male':
        gender = 'Male'
    if gender == 'F' or 'female':
        gender = 'Female'
    return gs[gender]

def format_age(options, age):
    units = options['host_age_unit']
    if age.find(' ') == -1:
        age = age[:-1] + ' ' + age[-1]
    val, unit = age.split()
    unit = unit.lower()
    if unit == 'y' or unit == 'year':
        unit = 'Years'
    elif unit == 'm' or unit == 'month':
        unit = 'Months'
    elif unit == 'd' or unit == 'day':
        unit = 'Days'
    elif unit == 'w' or unit == 'week' or unit == 'wk':
        unit = 'Weeks'
    elif unit == 'h' or unit == 'hour':
        unit = 'Hours'
    return int(val), units[unit]

def format_hospitalized(options, hospitalized):
    status = options['host_health_status']
    return status[hospitalized]

def load_phenotypes(sample_id):
    sample_id = sample_id[:2] + sample_id[3:]
    phenotypes = []
    filename = f'data/vitek_csvs/{sample_id}-1.csv'
    if not os.path.exists(filename):
        print(sample_id, 'None')
        return None
    with open(filename) as f:
        lines = f.read().splitlines()
    read = False
    for line in lines:
        if line.find('Antimicrobial') != -1:
            read = True
            continue
        if read:
            it = [x for x in line.split(',')[1:] if x and x != '«']
            if len(it) == 3 and it[0] not in ['NEG', 'POS']:
                d1 = it[0]
                mic = it[1]
                ip = it[2]
                phenotypes.append((d1, mic, ip))
            elif len(it) == 6:
                d1 = it[0]
                mic = it[1]
                ip = it[2]
                phenotypes.append((d1, mic, ip))
                d2 = it[3]
                mic = it[4]
                ip = it[5]
                phenotypes.append((d2, mic, ip))
            elif len(it) == 4:
                phenotypes.append((it[0], it[1], it[2]))
            elif len(it) == 5 and it[0] == 'Clindamycin':
                phenotypes.append((it[0], it[1], it[2]))
                phenotypes.append(('Trimethoprim/Sulfamethoxazole', it[3], it[4]))
            elif it[0] == 'NEG' or it[0] == 'POS':
                phenotypes.append(('Inducible Clindamycin Resistance', it[0], it[1]))
            else:
                if len(it) > 1:
                    print(sample_id, it)
    sus = []
    with open('uploader/options.yml') as f:
        options = yaml.load(f, Loader=yaml.FullLoader)
    drugs = options['antimicrobial_agent']
    inter = options['interpretation']
    for d, mic, ip in phenotypes:
        ip = ip.strip(' *')
        if d == 'Cefoxitin Screen':
            ip = 'R' if mic == 'POS' else 'S'
            d = 'Cefoxitin'
        if d in drugs:
            sus.append({
                'antimicrobial_agent': drugs[d],
                'mic': mic,
                'interpretation': inter[ip]
            })
        
    return {'susceptibility': sus}
  
if __name__ == '__main__':
    main()
