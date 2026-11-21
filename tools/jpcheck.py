"""jpcheck.py: release gate for Japanese left in the English build (the skill's `jp_left.py` idea, per file).

    python -X utf8 tools/jpcheck.py [--build build/fd2_en_files] [--list]

1. Rows: every script/ row whose JP has kana/kanji has an `en` with none (runtime placeholders such as ＜勇者名＞,
   which the game swaps for a name, don't count), unless script/keep_jp.txt lists it (kept on purpose, with the
   reason; tools/lint.py enforces the same).
2. Binaries: the built EXE and every SSB_DATA/FD2BN entry the build changed are scanned for Shift-JIS runs
   (`scantext.spans`: 3+ double-byte characters with a kana). English is drawn with pair glyphs whose codes can
   decode as kana, so a run counts only when its bytes also occur in the ORIGINAL copy of that file or entry
   (Japanese the build left in place). Allowed: runs of keep_jp rows, and in the EXE and overlays runs inside the
   original slot of a translated row: `codetext` moved that string to the heap and re-pointed every reference, so
   the old bytes have no reader (tests/test_codetext.py checks "no reader left" on every vacated address).
   Unchanged entries hold no row text (step 1 would have caught it); GRPDATA and the FMVs hold no SJIS text.
Exit 1 when anything else is left.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches as B  # noqa: E402
import codetext  # noqa: E402
import lkf  # noqa: E402
import scantext  # noqa: E402

JP = re.compile(r"[぀-ヿ一-鿿]")
TAG = re.compile(r"\{[^{}]*\}")
ORIG = ROOT / "work" / "disc" / "tree"
EXE = "SLPS_027.54"
EXE_PAD = 0x10000     # tools/build.py: string heap inserted after the 0x800-byte PS-X EXE header
HEAD = 0x800
EXE_CHAR_LISTS = (0x5E9D9, 0x5EFE9)   # docs/re/text.md: two SJIS character lists in the EXE (original offsets)
EVX_LABEL_END = 0x22                  # EVX header: u16, then the dev label field up to 0x22 (script/evx `dev label`)


def strip(s):
    s = TAG.sub("", s)
    for t in B.GAME_TAGS:
        s = s.replace(t, "")
    return s


def keep_ids():
    p = ROOT / "script" / "keep_jp.txt"
    return {ln.split("\t", 1)[0].strip() for ln in p.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")}


def check_rows(keep):
    bad, kept_jp, done = [], [], {}
    for p in B.files():
        for r in B.read_tsv(p):
            rid, jp, en = r[0], r[1], (r[2] if len(r) > 2 else "")   # en " " is real (rfd2.8009D9E4 ね。)
            if rid.split(".")[0] in ("SLPS", "op", "rfd2", "ed", "pro") and en:
                done.setdefault(rid.split(".")[0], set()).add(int(rid.split(".")[1], 16))
            if not JP.search(strip(jp)):
                continue
            if rid in keep:
                kept_jp.append(TAG.sub("", jp))
                continue
            if not en or JP.search(strip(en)):
                bad.append(f"{p.relative_to(ROOT).as_posix()} {rid}: en={en[:40]!r}")
    return bad, kept_jp, done


def slots(data, base, vaddrs):
    """[start, end) file offsets of the original strings at these vaddrs."""
    out = []
    for v in vaddrs:
        o = v - base
        if 0 <= o < len(data):
            end = data.find(b"\0", o)
            out.append((o, end if end > o else o + 1))
    return out


def allowed(label, start, s, data):
    """Japanese-looking bytes that are not text the game shows."""
    if label.endswith(".EVX") and start < EVX_LABEL_END:
        return True     # tail of the EVX dev label field (the English label ends in a NUL before it; never shown)
    if label == EXE and any(a <= start < data.find(b"\0", a) for a in EXE_CHAR_LISTS):
        return True     # SJIS character lists (font code tables, docs/re/text.md), not strings
    # the placeholder names rfd2 strncmps (its tag table); a scan can start mid-character before one ("ヲn方名＞")
    return not JP.search(strip(s)) or any(s[-3:] == t[-3:] and len(s) <= len(t) + 1 for t in B.GAME_TAGS)


def leftovers(built, orig, kept_jp, label, vacated=()):
    """Runs in `built` whose bytes also occur in `orig`, neither kept on purpose nor in a vacated slot."""
    found = []
    for start, end, s in scantext.spans(built):
        if built[start:end].rstrip(b" ") not in orig:
            continue
        if any(s in k or k in s for k in kept_jp if len(k) >= 2) or allowed(label, start, s, built):
            continue
        tag = " vacated" if any(a <= start < b for a, b in vacated) else ""
        found.append((label + tag, start, s))
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", default=str(ROOT / "build" / "fd2_en_files"))
    ap.add_argument("--list", action="store_true", help="print every run found, vacated ones too")
    a = ap.parse_args(argv)
    build = Path(a.build)
    keep = keep_ids()
    bad, kept_jp, done = check_rows(keep)
    print(f"rows: {len(bad)} with Japanese and no English (keep_jp.txt: {len(keep)} kept on purpose)")
    for line in bad[:30]:
        print("  " + line)

    runs = []
    exe_b, exe_o = (build / EXE).read_bytes(), (ORIG / EXE).read_bytes()
    body = exe_b[:HEAD] + exe_b[HEAD + EXE_PAD:]          # the original layout: offsets = original offsets
    runs += leftovers(exe_b[HEAD:HEAD + EXE_PAD], exe_o, kept_jp, f"{EXE} heap")
    runs += leftovers(body, exe_o, kept_jp, EXE, slots(exe_o, codetext.EXE_BASE, done.get("SLPS", ())))
    for arc in ("SSB_DATA.LKF", "FD2BN.LKF"):
        new = dict((e["name"], d) for e, d in lkf.files((build / arc).read_bytes()))
        old = dict((e["name"], d) for e, d in lkf.files((ORIG / arc).read_bytes()))
        for name, d in new.items():
            o = old.get(name, b"")
            if o == d:
                continue
            ovl = name[:-4] if name in codetext.OVERLAYS else None
            vac = slots(o, codetext.OVL_BASE, done.get(ovl, ())) if ovl else ()
            runs += leftovers(d, o, kept_jp, f"{arc}/{name}", vac)
    hard = [r for r in runs if not r[0].endswith("vacated")]
    print(f"binaries: {len(runs)} original Japanese runs left in changed files, {len(runs) - len(hard)} of them in"
          f" vacated slots of relocated strings (no reader)")
    for label, start, s in (runs if a.list else hard[:30]):
        print(f"  {label} +{start:#x}: {s[:40]}")
    ok = not bad and not hard
    print("jpcheck: " + ("ok" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
