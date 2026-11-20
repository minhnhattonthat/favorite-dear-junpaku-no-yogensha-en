"""retools.py: PS1 EXE recon helpers (capstone MIPS disassembly, lui/addiu xrefs). Not named re.py: that shadows
the stdlib `re` when run from tools/.

    python -X utf8 tools/retools.py dis  EXE VADDR [COUNT]     disassemble COUNT instructions at VADDR
    python -X utf8 tools/retools.py xref EXE VADDR [END]       code that builds VADDR (or any address < END) with lui + addiu/ori/lw/sw...
    python -X utf8 tools/retools.py va   EXE FILEOFF           file offset -> vaddr

EXE paths are PS-X EXE files (2048-byte header, t_addr at 0x18)."""
import struct
import sys

import capstone


class Exe:
    def __init__(self, path):
        self.data = open(path, "rb").read()
        self.base = struct.unpack_from("<I", self.data, 0x18)[0]

    def off(self, va):
        return va - self.base + 0x800

    def va(self, off):
        return off - 0x800 + self.base

    def word(self, va):
        return struct.unpack_from("<I", self.data, self.off(va))[0]

    def dis(self, va, count=32):
        md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32 + capstone.CS_MODE_LITTLE_ENDIAN)
        o = self.off(va)
        return list(md.disasm(self.data[o:o + 4 * count], va))

    def xref(self, target, end=None):
        """Find lui rX,hi followed within 16 instructions by an op on rX with lo, giving target
        (or any address in [target, end) when end is given)."""
        end = target + 1 if end is None else end
        hits = []
        d = self.data
        n = len(d)
        for o in range(0x800, n - 4, 4):
            w = struct.unpack_from("<I", d, o)[0]
            if w >> 26 != 0x0F:  # lui
                continue
            rt = (w >> 16) & 31
            hi = (w & 0xFFFF) << 16
            for k in range(1, 17):
                o2 = o + 4 * k
                if o2 + 4 > n:
                    break
                w2 = struct.unpack_from("<I", d, o2)[0]
                op = w2 >> 26
                rs = (w2 >> 21) & 31
                if rs != rt:
                    continue
                imm = w2 & 0xFFFF
                if op in (0x09, 0x23, 0x21, 0x20, 0x24, 0x25, 0x2B, 0x29, 0x28):  # addiu, lw, lh, lb, lbu, lhu, sw, sh, sb
                    val = (hi + (imm - 0x10000 if imm & 0x8000 else imm)) & 0xFFFFFFFF
                elif op == 0x0D:  # ori
                    val = hi | imm
                else:
                    continue
                if target <= val < end:
                    hits.append((self.va(o2), val))
        return hits


def main(argv):
    cmd, path = argv[0], argv[1]
    e = Exe(path)
    if cmd == "dis":
        for i in e.dis(int(argv[2], 16), int(argv[3]) if len(argv) > 3 else 32):
            print(f"{i.address:08x}  {i.mnemonic:8} {i.op_str}")
    elif cmd == "xref":
        end = int(argv[3], 16) if len(argv) > 3 else None
        for h, val in e.xref(int(argv[2], 16), end):
            print(f"{h:08x}  -> {val:08x}")
    elif cmd == "va":
        print(f"{e.va(int(argv[2], 16)):08x}")


if __name__ == "__main__":
    main(sys.argv[1:])
