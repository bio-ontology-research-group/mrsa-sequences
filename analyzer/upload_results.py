import click as ck
import subprocess
import json
import os

@ck.command()
def main():
    with open('state.json') as f:
        state = json.loads(f.read())
    for sample_id in state:
        sid = sample_id[-3:]
        res_dir = f'/home/kulmanm/data/mrsa_analysis/MRSA{sid}/'
        if not os.path.exists(res_dir):
            continue
        res_files = os.listdir(res_dir)
        res_files = [f'{res_dir}{f}' for f in res_files]
        cmd = [
            'arv-put', '--project-uuid', 'cborg-j7d0g-lcux1tdrdshvul7',
            '--name', f'Output collection for MRSA{sid}']
        cmd += res_files
        proc = subprocess.run(cmd, capture_output=True)
        if proc.returncode == 0:
            output_col = proc.stdout.decode('utf-8').strip()
            state[sample_id]['output_collection'] = output_col
            state[sample_id]['status'] = 'complete'
        else:
            output = proc.stderr.decode('utf-8')
            print(output)

    with open('state.json', 'w') as f:
        f.write(json.dumps(state))

if __name__ == '__main__':
    main()
