"""extract.py: every text source on the disc -> script/*.tsv (columns id, jp, en, notes).

    python -X utf8 tools/extract.py [--force]

Re-running keeps `en` and `notes` of existing rows and refuses to drop a row that has an `en` unless --force.
The `jp` column round-trips byte-exact: Source.build(original, {id: jp text}) == original (tests/test_text.py),
and the insert step calls the same build with the `en` texts.

Sources (docs/re/text.md): SSB_DATA *.MSG (msg.py), *.ssb (ssb.py), *.EVX (evx.py), *.end (misctext.py),
GRPDATA Dummy00.DAT (misctext.py), the EXE and the text overlays op/rfd2/ed/pro.bin in FD2BN (codetext.py).
Text form: jtext.py, plus {n} {wait} {clear} for line break, key wait and new page in every format."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import codetext  # noqa: E402
import evx  # noqa: E402
import jtext  # noqa: E402
import lkf  # noqa: E402
import misctext  # noqa: E402
import msg  # noqa: E402
import ssb  # noqa: E402

TREE = ROOT / "work/disc/tree"
SCRIPT = ROOT / "script"
COLS = ["id", "jp", "en", "notes"]
EXE = "SLPS_027.54"
END_TAGS = {"n": b"\r\n"}


class Row:
    """raw = the row's original bytes, found at file offset `off`."""
    __slots__ = ("id", "raw", "off", "jp", "notes")

    def __init__(self, id, raw, off, jp, notes=""):
        self.id, self.raw, self.off, self.jp, self.notes = id, raw, off, jp, notes


class Source:
    """One file's text. where = ("lkf", archive, entry name) or ("file", disc file name).
    skip: byte ranges known to be structure (tables, op headers) for the coverage test."""

    def __init__(self, tsv, where, data, rows, builder, encoder, skip=()):
        self.tsv, self.where, self.data, self.rows = tsv, where, data, rows
        self._build, self._encode = builder, encoder
        self.skip = list(skip)

    def encode(self, row_id, text):
        return self._encode(row_id, text)

    def build(self, texts):
        """File bytes with rows replaced: texts = {row id: text form}; rows not given keep their bytes."""
        return self._build({i: self.encode(i, t) for i, t in texts.items()})


def _stem(entry):
    return entry.rsplit(".", 1)[0]


def _msg_source(entry, data):
    bank = msg.parse(entry, data)
    stem = _stem(entry)
    rows = []
    for key, raw in bank.strings:
        note = "speaker" if key.endswith("S") else ""
        off = int(key.rstrip("S"), 16)
        rows.append(Row(f"{stem}.{key}", raw, off, jtext.decode(raw), note))
    keys = {f"{stem}.{k}": k for k, _ in bank.strings}

    def build(new):
        b = msg.parse(entry, data)
        b.replace({keys[i]: v for i, v in new.items()})
        return msg.build(b)

    return Source(SCRIPT / "msg" / f"{stem}.tsv", ("lkf", "SSB_DATA", entry), data, rows, build,
                  lambda i, t: jtext.encode(t), skip=[(0, bank.meta["header"])])


def _ssb_source(entry, data):
    stem = _stem(entry)
    rows, kinds = [], {}
    for off, kind, raw in ssb.rows(data):
        rid = f"{stem}.{off:04X}"
        kinds[rid] = (off, kind)
        start = off + 4 if kind == "name" else off  # a name row's bytes follow its op (argc, 0x19, u16 count)
        rows.append(Row(rid, raw, start, ssb.decode_row(raw, kind), "speaker" if kind == "name" else ""))
    toks, _ = ssb.parse(data)
    skip = [(0, ssb.HEADER)]
    for k, o, v in toks:
        if k == "op":
            skip.append((o, o + 2 + 2 * len(v[1])))
        elif k == "raw":
            skip.append((o, o + len(v)))
    return Source(SCRIPT / "ssb" / f"{stem}.tsv", ("lkf", "SSB_DATA", entry), data, rows,
                  lambda new: ssb.build(data, {kinds[i][0]: v for i, v in new.items()}),
                  lambda i, t: ssb.encode_row(t, kinds[i][1]), skip=skip)


def _evx_source(entry, data):
    stem = _stem(entry)
    info = evx.parse(data)
    rows = [Row(f"{stem}.{k}", raw, int(k, 16), jtext.decode(raw),
                {"title": "dev label (guess: not shown)", "unit": "unit name (32-byte field)"}.get(kind, kind))
            for k, kind, raw in info["strings"]]
    return Source(SCRIPT / "evx" / f"{stem}.tsv", ("lkf", "SSB_DATA", entry), data, rows,
                  lambda new: evx.build(data, {i.split(".", 1)[1]: v for i, v in new.items()}),
                  lambda i, t: jtext.encode(t))


def _end_text(raw):
    return jtext.decode(raw).replace("{0D}{0A}", "{n}")


def _end_sources(entry, data):
    stem = _stem(entry)
    rows = [Row(f"{stem}.{o:04X}", raw, o, _end_text(raw)) for o, raw in misctext.end_rows(data)]
    return Source(SCRIPT / "end" / f"{stem}.tsv", ("lkf", "SSB_DATA", entry), data, rows,
                  lambda new: misctext.end_build(data, {int(i.split(".")[1], 16): v for i, v in new.items()}),
                  lambda i, t: jtext.encode(t, tags=END_TAGS))


def _rec_source(entry, data):
    stem = _stem(entry)
    rows = [Row(f"{stem}.{o:04X}", raw, o, jtext.decode(raw), "fixed 48-byte record (guess: unused file)")
            for o, raw in misctext.rec_rows(data)]
    return Source(SCRIPT / "misc" / f"{stem}.tsv", ("lkf", "GRPDATA", entry), data, rows,
                  lambda new: misctext.rec_build(data, {int(i.split(".")[1], 16): v for i, v in new.items()}),
                  lambda i, t: jtext.encode(t))


def _ref_note(e):
    kinds = [r[0] for r in e["refs"]]
    if kinds and kinds[0] == "tab":
        va, stride, _ = e["refs"][0][1:]
        return f"table {va:08X} stride {stride:#x}"
    return " ".join(f"{k}x{kinds.count(k)}" for k in dict.fromkeys(kinds))


def _code_source(name, where, data, tsv, prefix):
    base = codetext.base_of(name)
    found = codetext.strings(name, data)
    rows = [Row(f"{prefix}.{base + o:08X}", e["bytes"], o, jtext.decode(e["bytes"]), _ref_note(e))
            for o, e in found.items()]
    offs = {r.id: r.off for r in rows}
    return Source(tsv, where, data, rows,
                  lambda new: codetext.replace_in_place(data, {offs[i]: v for i, v in new.items()}),
                  lambda i, t: jtext.encode(t))


def sources(tree=TREE):
    """Every text Source, from the unpacked original disc."""
    out = []
    for e, data in lkf.files((tree / "SSB_DATA.LKF").read_bytes()):
        name, ext = e["name"], e["name"].rsplit(".", 1)[-1].lower()
        make = {"msg": _msg_source, "ssb": _ssb_source, "evx": _evx_source, "end": _end_sources}.get(ext)
        assert make, f"SSB_DATA entry {name}: unknown type"
        out.append(make(name, data))
    for e, data in lkf.files((tree / "GRPDATA.LKF").read_bytes()):
        if e["name"] == "Dummy00.DAT":
            out.append(_rec_source(e["name"], data))
    for e, data in lkf.files((tree / "FD2BN.LKF").read_bytes()):
        if e["name"] in codetext.OVERLAYS:
            stem = _stem(e["name"])
            out.append(_code_source(e["name"], ("lkf", "FD2BN", e["name"]), data, SCRIPT / "ovl" / f"{stem}.tsv", stem))
    exe = (tree / EXE).read_bytes()
    out.append(_code_source(EXE, ("file", EXE), exe, SCRIPT / "exe.tsv", "SLPS"))
    return out


def read_tsv(path):
    """plain tab-separated, no quoting; every row must have len(COLS) fields"""
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    head = lines[0].split("\t")
    if head != COLS:
        raise ValueError(f"{path}: header {head} != {COLS}")
    rows = []
    for n, line in enumerate(lines[1:], 2):
        rec = line.split("\t")
        if len(rec) != len(COLS):
            raise ValueError(f"{path}:{n}: {len(rec)} columns, want {len(COLS)}")
        rows.append(dict(zip(COLS, rec)))
    return rows


def write_tsv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    out = ["\t".join(COLS)]
    for r in rows:
        rec = [r.get(c, "") for c in COLS]
        if any("\t" in v or "\n" in v or "\r" in v for v in rec):
            raise ValueError(f"{r['id']}: tab or newline in a field")
        out.append("\t".join(rec))
    data = "\n".join(out) + "\n"
    if not path.exists() or path.read_text(encoding="utf-8") != data:
        path.write_text(data, encoding="utf-8", newline="\n")


def merge(path, rows, force):
    """keep en/notes of existing rows; refuse to lose a translated row unless force"""
    old = {r["id"]: r for r in read_tsv(path)} if path.exists() else {}
    new_ids = {r.id for r in rows}
    lost = [i for i, r in old.items() if i not in new_ids and r["en"]]
    if lost and not force:
        raise SystemExit(f"{path}: would drop translated rows {lost[:5]}... (use --force)")
    out = []
    for r in rows:
        o = old.get(r.id)
        out.append(dict(id=r.id, jp=r.jp, en=o["en"] if o else "", notes=o["notes"] if o and o["notes"] else r.notes))
    write_tsv(path, out)
    return len(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    srcs = sources()
    paths = [s.tsv for s in srcs]
    assert len(set(paths)) == len(paths), "two sources share a TSV"
    n = sum(merge(s.tsv, s.rows, a.force) for s in srcs if s.rows or s.tsv.exists())
    print(f"{len(srcs)} sources ({sum(1 for s in srcs if s.rows)} with text), {n} rows -> {SCRIPT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
