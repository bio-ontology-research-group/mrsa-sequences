import click as ck
import json
import os
import pandas as pd

def main():
    
    files = os.listdir('data/snippy')
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

    mo_bad_samples = set([
        'ID00070', 'ID00187', 'ID00212', 'ID00243', 'ID00247',
        'ID00261', 'ID00314', 'ID00323', 'ID00349', 'ID00355',
        'ID00356', 'ID00357', 'ID00360', 'ID00361', 'ID00372',
        'ID00384', 'ID00390', 'ID00413', 'ID00442', 'ID00466',
        'ID00477', 'ID00478', 'ID00481', 'ID00491', 'ID00500',
        'ID00501', 'ID00502', 'ID00503', 'ID00506', 'ID00507',
        'ID00508', 'ID00509', 'ID00510', 'ID00511', 'ID00512',
        'ID00527', 'ID00559', 'ID00560', 'ID00563', 'ID00568',
        'ID00569', 'ID00574', 'ID00579', 'ID00581', 'ID00582',
        'ID00585', 'ID00589', 'ID00590', 'ID00592', 'ID00597',
        'ID00600', 'ID00601', 'ID00602', 'ID00604', 'ID00605',
        'ID00608', 'ID00609', 'ID00619', 'ID00629', 'ID00635',
        'ID00643', 'ID00645', 'ID00660', 'ID00661', 'ID00662',
        'ID00664', 'ID00667', 'ID00668', 'ID00671', 'ID00672',
        'ID00692', 'ID00693', 'ID00711', 'ID00717', 'ID00730',
        'ID00736', 'ID00745', 'ID00747', 'ID00755', 'ID00758',
        'ID00760', 'ID00763', 'ID00773', 'ID00775', 'ID00776',
        'ID00778', 'ID00780', 'ID00812', 'ID00813', 'ID00814',
        'ID00815', 'ID00818', 'ID00820', 'ID00826', 'ID00827',
        'ID00829', 'ID00830', 'ID00837', 'ID00838', 'ID00840',
        'ID00841', 'ID00842', 'ID00843', 'ID00844', 'ID00845',
        'ID00848', 'ID00851', 'ID00856', 'ID00861', 'ID00869',
        'ID00872', 'ID00873', 'ID00874', 'ID00875', 'ID00876',
        'ID00877'])

    bad_samples |= core_bad_samples
    bad_samples |= mo_bad_samples
    
    # samples = []
    # for s_id in files:
    #     if s_id in bad_samples:
    #         continue
    #     with open(f'data/snippy/{s_id}/snps.vcf') as f:
    #         variants = 0
    #         for line in f:
    #             if not line.startswith('#'):
    #                 variants += 1
    #     # Kraken
    #     score, tax_id, tax_name = get_kraken_report(s_id)
    #     if variants > 0 and tax_id == '1280' and score > 70:
    #         samples.append(s_id)
    #     else:
    #         bad_samples.add(s_id)

    
    # samples = sorted(samples)
    
    df = pd.read_csv('data/SA04.csv')
    samples = set(df['UID'])

    samples -= core_bad_samples
    
    inputobj = {
        "gff_files": [
            {
                "class": "File",
                "location": "data/Reference.gff"
            },
        ],
        "reference": {
            "class": "File",
            "location": "data/reference.fasta"
        },
        "reference_gb": {
            "class": "File",
            "location": "data/reference.gb"
        },
        "metadata": {
            "class": "File",
            "location": "data/metadata.tsv"
        },
        "dirs": [],
        "snippy_inprefix": "snps"
    }
    for s_id in samples:
        inputobj["gff_files"].append({
            "class": "File",
            "location": f'data/prokka/{s_id}.gff'})
        inputobj["dirs"].append({
            "class": "Directory",
            "location": f'data/snippy/{s_id}'})
    
    print('Updated pangenome input file pangenome.json')
    with open('pangenome.json', 'w') as f:
        f.write(json.dumps(inputobj))



def get_kraken_report(s_id):
    result = []
    with open(f'data/kraken/{s_id}.tsv', "r") as f:
        for line in f:
            it = line.strip().split('\t')
            if it[3] == 'S':
                result.append((float(it[0]), it[4], it[5].strip()))
                if len(result) == 4:
                    break
    while len(result) < 4:
        result.append((0.0, '-', '-'))
    return result[0]


if __name__ == '__main__':
    main()


