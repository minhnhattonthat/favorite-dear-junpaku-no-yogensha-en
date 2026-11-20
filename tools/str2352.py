"""str2352.py: wrap a dumpsxiso-extracted .STR (2336-byte Mode2 sectors: subheader + data) as 2352-byte raw
sectors (sync + header added), which ffmpeg's psxstr demuxer reads.

    python tools/str2352.py work/disc/tree/ENDING.STR work/fmv/ENDING.raw
    ffmpeg -f psxstr -i work/fmv/ENDING.raw -vf fps=1 work/fmv/ending/f%04d.png

Recon only (the header's MSF is a dummy); not used by the build."""
import sys

SYNC = b"\x00" + b"\xff" * 10 + b"\x00"


def main(src, dst):
    with open(src, "rb") as f, open(dst, "wb") as g:
        n = 0
        while True:
            s = f.read(2336)
            if len(s) < 2336:
                break
            g.write(SYNC + b"\x00\x02\x00\x02" + s)
            n += 1
    print(f"{dst}: {n} sectors")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
