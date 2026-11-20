"""voices.py: per-speaker voice markers and paired JP/EN examples, for docs/style-reference.md and reviews.

    python -X utf8 tools/voices.py                 speakers with >= 30 lines: line count, top markers
    python -X utf8 tools/voices.py SPEAKER [N]     N example JP/EN pairs (default 6) with the most markers

Speakers come from the batch files' speaker column (ssb/EVX name tags), so fairy reports and other untagged files
are not covered; read those by file (FryMsgN = fairy N).
"""
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import batches as B  # noqa: E402

MARKERS = ["俺", "オレ", "僕", "ボク", "私", "わたし", "あたし", "アタシ", "ワシ", "わし", "儂", "拙者", "余", "我",
           "わたくし", "うち", "じゃ", "ぜ", "ぞ", "のう", "ですぅ", "ですわ", "のです", "ですの", "かしら", "わね",
           "わよ", "だわ", "ねぇ", "っす", "でございます", "ござる", "おる", "てめえ", "貴様", "お前", "あなた",
           "君", "あんた", "ちゃん", "よな", "だろ", "なのだ", "である"]


def rows():
    for p in sorted(B.BATCHES.glob("b*.tsv")):
        en = {r[0]: r[1] for r in B.read_tsv(B.OUT / p.name)}
        for rid, kind, spk, jp in B.read_tsv(p):
            if spk and kind.startswith("wrap") and en.get(rid, "-") != "-":
                yield spk, rid, jp, en[rid]


def markers(jp):
    return [m for m in MARKERS if m in jp]


def main(argv):
    data = {}
    for spk, rid, jp, en in rows():
        data.setdefault(spk, []).append((rid, jp, en))
    if not argv:
        for spk, lst in sorted(data.items(), key=lambda kv: -len(kv[1])):
            if len(lst) < 30:
                continue
            c = Counter(m for _, jp, _ in lst for m in markers(jp))
            print(f"{spk}\t{len(lst)}\t" + " ".join(f"{m}:{n}" for m, n in c.most_common(8)))
        return 0
    spk, n = argv[0], int(argv[1]) if len(argv) > 1 else 6
    lst = sorted(data.get(spk, []), key=lambda r: (-len(markers(r[1])), len(r[1])))
    for rid, jp, en in [r for r in lst if 15 < len(r[1]) < 90][:n]:
        print(f"{rid}\n  JP: {B.TAG.sub(' ', jp)}\n  EN: {B.TAG.sub(' ', en)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
