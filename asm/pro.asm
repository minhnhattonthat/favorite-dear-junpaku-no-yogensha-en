; pro.asm: name entry (FD2BN pro.bin, loaded at 0x8009B4B0). armips, run by tools/build.py (patch_pro):
;   armips asm/pro.asm -strequ PRO_IN <in> -strequ PRO_OUT <out>
; 1. The default name: the entry state keeps the name as kana-grid indices (u8 x 6 at +0x5E4, 0xFE = empty;
;    length u16 at +0x5E2). The original set ラビエル (C6 E1 A3 C8 FE FE, length 4) at two places; now
;    "Raviel" (grid: Ａ-Ｚ = 0-25, ａ-ｚ = 32-57 in the 256-character table at 0x800A1864), stored as halfwords.
; 2. The commit memcpy(0x8007F480, entry + 0x612, 12) -> name_commit (asm/name.asm, EXE FREE block).

.psx
.include "addrs.inc"
.open PRO_IN, PRO_OUT, 0x8009B4B0

GRID_R  equ 17
GRID_a  equ 32

.macro default_name, base
    ori     v0, zero, (GRID_a << 8) | GRID_R        ; R a
    sh      v0, 0x5E4(base)
    ori     v0, zero, ((GRID_a + 8) << 8) | (GRID_a + 21)   ; v i
    sh      v0, 0x5E6(base)
    ori     v0, zero, ((GRID_a + 11) << 8) | (GRID_a + 4)   ; e l
    sh      v0, 0x5E8(base)
    nop
    nop
    nop
    nop
    nop
    addiu   v0, zero, 6
.endmacro

.org 0x8009BF80                         ; new game: entry init (base s2); jal 0x8009E554 / sh v0,0x5E2(s2) follow
    default_name s2
.org 0x8009BFB0
    jal     0x8009E554
    sh      v0, 0x5E2(s2)

.org 0x8009D7F4                         ; entry reset (base a0 = s2)
    default_name a0
.org 0x8009D824
    jal     0x8009E554
    sh      v0, 0x5E2(a0)

.org 0x8009CBAC                         ; commit: memcpy(a0 = 0x8007F480, a1 = entry + 0x612, a2 = 12)
    jal     NAME_COMMIT

.close
