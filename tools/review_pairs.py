"""review_pairs.py: pairs files for the per-batch reviewer pass (`references/translation.md` §Review).

    python -X utf8 tools/review_pairs.py [bNNN ...]     -> work/qa/review/pairs/bNNN.txt (all batches by default)

Each entry: `>> id | speaker | kind`, then `JP:` and `EN:` lines; rows keep the batch's script order, so the rows
around an entry are its context. A reviewer writes `work/qa/review/bNNN.md` with Critical/Important/Minor by id;
Critical/Important get fixed in trans/en, Minors go to docs/polish.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import batches as B  # noqa: E402

OUTDIR = B.ROOT / "work" / "qa" / "review" / "pairs"


def write(b):
    en = {r[0]: r[1] for r in B.read_tsv(B.OUT / f"{b}.tsv")}
    out = [f"# {b}: {len(en)} rows. Glossary: glossary.md; voices: docs/style-reference.md; story: docs/synopsis.md",
           ""]
    for rid, kind, spk, jp in B.read_tsv(B.BATCHES / f"{b}.tsv"):
        out += [f">> {rid} | {spk or '-'} | {kind}", f"JP: {jp}", f"EN: {en.get(rid, '(missing)')}", ""]
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / f"{b}.txt").write_text("\n".join(out), encoding="utf-8", newline="\n")


def main(argv):
    names = argv or sorted(p.stem for p in B.BATCHES.glob("b*.tsv"))
    for b in names:
        write(b)
    print(f"{len(names)} pairs files -> {OUTDIR.relative_to(B.ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
