import pandas as pd
import click as ck



@ck.command()
def main():
    samples, seqs = read_fasta('data/mecas-aligned.fa')
    for i in range(7, len(samples)):
        gen_snps(samples[i], seqs[0], seqs[i])
        break

def gen_snps(sample_id, ref, seq):
    print(sample_id)
    for i in range(len(ref)):
        r = ref[i]
        a = seq[i]
        if r != '-' and a !='-' and r != a:
            print(sample_id, i + 1, r, a)


def read_fasta(filename):
    seqs = list()
    info = list()
    seq = ''
    inf = ''
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if seq != '':
                    seqs.append(seq)
                    info.append(inf)
                    seq = ''
                inf = line[1:]
            else:
                seq += line
        seqs.append(seq)
        info.append(inf)
    return info, seqs

    
if __name__ == '__main__':
    main()
