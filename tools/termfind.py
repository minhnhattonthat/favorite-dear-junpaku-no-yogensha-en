"""Show how JP terms were already translated: `python -X utf8 tools/termfind.py ガラルス デーバ [-n 2]`.

Scans trans/batches (JP) against trans/en (EN) and prints the hit count and the first N translated rows per term.
"""
import csv
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(pattern, col):
    out = {}
    for f in glob.glob(os.path.join(ROOT, pattern)):
        with open(f, encoding='utf-8', newline='') as fh:
            for r in csv.reader(fh, delimiter='\t'):
                if len(r) > col:
                    out[r[0]] = r[col]
    return out


def main(argv):
    n = 2
    if '-n' in argv:
        i = argv.index('-n')
        n = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    jp = load('trans/batches/*.tsv', 3)
    en = load('trans/en/*.tsv', 1)
    for t in argv:
        hits = [(i, en[i]) for i, j in jp.items() if t in j and i in en and en[i] != '-']
        print(t, len(hits))
        for i, e in hits[:n]:
            print('   ', i, e[:200])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
