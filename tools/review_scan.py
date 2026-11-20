"""Review helpers over trans/batches + trans/en (read-only).

  review_scan.py names            near-miss capitalised words (edit distance 1, one side rare): "Suole"/"Suore"
  review_scan.py kata             katakana terms whose usual English is missing from some rows
  review_scan.py angel            lines that gender the angel (he/she after "the angel")
  review_scan.py ratio [N]        the N rows with the shortest EN for their JP (omissions)
  review_scan.py grep REGEX       rows whose JP or EN matches
  review_scan.py sample SEED N W PREFIX_REGEX   N random W-row windows of dialogue, JP / EN
"""
import collections, csv, random, re, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load():
    rows = {}
    for p in sorted((ROOT / "trans/batches").glob("b*.tsv")):
        with open(p, encoding="utf-8") as f:
            src = {r[0]: r for r in list(csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE))[1:]}
        en = ROOT / "trans/en" / p.name
        if not en.exists():
            continue
        with open(en, encoding="utf-8") as f:
            for r in list(csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE))[1:]:
                if r[0] in src:
                    rows[r[0]] = (p.stem, src[r[0]][1], src[r[0]][2], src[r[0]][3], r[1])
    return rows


def compact(s):
    return re.sub(r"\{wait\}\{clear\}", " / ", s).replace("＄＄＄＄＄＄", "$P").replace("{n}", " ")


def ed1(a, b):
    if abs(len(a) - len(b)) > 1:
        return 9
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (ca != cb))
    return d[-1]


def main(argv):
    rows = load()
    mode = argv[0] if argv else "help"
    if mode == "names":
        cnt = collections.Counter(w for r in rows.values()
                                  for w in re.findall(r"\b[A-Z][a-z]{3,}\b", re.sub(r"\{[^}]*\}", " ", r[4])))
        for a in cnt:
            for b in cnt:
                if a < b and min(cnt[a], cnt[b]) <= 5 and a.rstrip("s") != b.rstrip("s") and ed1(a, b) == 1:
                    print(a, cnt[a], b, cnt[b])
    elif mode == "kata":
        kat = collections.defaultdict(list)
        for i, (b, k, sp, jp, en) in rows.items():
            if en.strip() != "-" and k != "name":
                for t in set(re.findall(r"[ァ-ヶ][ァ-ヶー・]{2,}", jp)):
                    kat[t].append(i)
        for t, ids in sorted(kat.items(), key=lambda x: -len(x[1])):
            c = collections.Counter(w for i in ids for w in set(re.findall(r"\b[A-Z][a-z]+\b", rows[i][4])))
            if len(ids) >= 3 and c:
                best, n = c.most_common(1)[0]
                miss = [i for i in ids if best not in rows[i][4]]
                if n >= 3 and 0 < len(miss) <= len(ids) / 3:
                    print(f"{t} -> {best} ({len(ids)}); missing in: {' '.join(miss[:6])}")
    elif mode == "angel":
        for i, r in rows.items():
            if re.search(r"\b(the|an|that|this) angel\b[^.?!]*\b(he|she|his|her|him|himself|herself)\b", r[4], re.I):
                print(i, "|", r[4][:200])
    elif mode == "ratio":
        def pl(s):
            return re.sub(r"\{[^}]*\}|＄＄＄＄＄＄|＜[^＞]*＞", "", s)
        rs = sorted((len(pl(r[4])) / len(pl(r[3])), i) for i, r in rows.items()
                    if len(pl(r[3])) >= 40 and r[4].strip() != "-")
        print("median EN/JP length", round(statistics.median(x for x, _ in rs), 2))
        for x, i in rs[:int(argv[1]) if len(argv) > 1 else 25]:
            print(f"{x:.2f} {i} {compact(rows[i][3])[:110]}\n   => {compact(rows[i][4])[:200]}")
    elif mode == "grep":
        pat = re.compile(argv[1])
        for i, r in rows.items():
            if pat.search(r[3]) or pat.search(r[4]):
                print(i, r[2], "|", compact(r[3])[:150], "|", compact(r[4])[:220])
    elif mode == "sample":
        seed, n, w, pat = int(argv[1]), int(argv[2]), int(argv[3]), argv[4]
        ids = [i for i in rows if re.match(pat, i) and rows[i][1].startswith("wrap")]
        random.seed(seed)
        for s in sorted(random.sample(range(len(ids) - w), n)):
            print("##", ids[s].split(".")[0])
            for i in ids[s:s + w]:
                print(f"{i.split('.')[1]} {rows[i][2]}: {compact(rows[i][3])}\n  > {compact(rows[i][4])}")
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
