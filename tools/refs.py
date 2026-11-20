"""refs.py: disassemble every reference to a string in the EXE or an overlay.

    python -X utf8 tools/refs.py rfd2.bin 0x8009D9E4 [--before 40] [--after 15]   (instructions around each site)
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import codetext  # noqa: E402
import extract  # noqa: E402
from capstone import CS_ARCH_MIPS, CS_MODE_LITTLE_ENDIAN, CS_MODE_MIPS32, Cs  # noqa: E402


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("va", type=lambda s: int(s, 16))
    ap.add_argument("--before", type=int, default=40)
    ap.add_argument("--after", type=int, default=15)
    a = ap.parse_args(argv)
    src = [s for s in extract.sources() if getattr(s, "code_name", "").lower() == a.file.lower()]
    if not src:
        sys.exit(f"no code source {a.file}")
    d, base = src[0].data, codetext.base_of(src[0].code_name)
    md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN)
    for site in codetext.ref_sites(src[0].code_name, d, a.va):
        o = site[-1]
        print(f"== {site[0]} at {base + o:#x}")
        lo = max(0, o - 4 * a.before)
        for i in md.disasm(d[lo:o + 4 * a.after], base + lo):
            print(f"{i.address:#x}{' >' if i.address == base + o else '  '} {i.mnemonic} {i.op_str}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
