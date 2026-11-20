; font.asm: English pair glyphs (docs/re/text.md §English font). armips, run by tools/build.py (patch_exe) on the
; EXE after it has prepended the FREE block (EXE t_addr moved down from 0x80020000 to FREE):
;   armips asm/font.asm -strequ EXE_IN <in> -strequ EXE_OUT <out> -equ PAIR_G <len(font_en.CHARS)>
;
; Font lookup 0x8002C474(code) binary-searches FD2Font.FPK's character list and returns the glyph index or -1.
; Hooked: a code that is not in the list but is a pair code (tools/font_en.py) returns 0x8000 | n. The glyph
; decoder 0x8002C5EC(index) writes a 12x14 4bpp cell to the buffer 0x80084578; hooked: index >= 0x8000 draws
; the two letters of pair n instead. The three callers that inlined the binary search (0x8002BF2C single glyph,
; 0x8002C080 and 0x8002C2B0 string-to-VRAM renderers) are patched to call the lookup, and the slot renderer
; 0x8002C514 no longer rejects an index above the glyph count.

.psx
.include "addrs.inc"
.open EXE_IN, EXE_OUT, (LOAD_ADDR - 0x800)  ; LOAD_ADDR (-equ, build.patch_exe): the moved t_addr, below FREE
                                            ; (the string heap of tools/codetext.py sits between them)

FREE      equ 0x8001E000                ; below the original load address: zero in every RAM dump (docs/re/space.md)
FREE_END  equ 0x80020000
LOOKUP    equ 0x8002C474
GLYPH     equ 0x8002C5EC
CELLBUF   equ 0x80084578

; --- lookup: not found -> try a pair code (v1 = code & 0xffff, a0 = list entry nearest the code)
.org 0x8002C500
    bne     a0, v1, pair_lookup
    nop
    jr      ra
    nop

; --- slot renderer: drop the "index > count" rejection (bltz still rejects -1)
.org 0x8002C548
    nop

; --- glyph decoder entry
.org GLYPH
    j       glyph_hook
    nop                                 ; replaced: addiu sp,-0x30 / lui v1,0x8008 (redone in the hook)

; --- dialogue layout (0x8002CC80 sets up 3 boxes x 24 cells and the name tag): cell advance 11 -> 12 px and
;     sprite width 10 -> 12 px, so a pair glyph shows all 12 columns with even 6 px letters
.org 0x8002CCD8
    addiu   s1, s1, 12                  ; dialogue: x += advance
.org 0x8002CCEC
    addiu   v0, zero, 12                ; dialogue: sprite w
.org 0x8002CDF0
    addiu   s1, s1, 12                  ; name tag: x += advance
.org 0x8002CE00
    addiu   v0, zero, 12                ; name tag: sprite w

; --- inline searches -> LOOKUP
.org 0x8002BF50                         ; single glyph into slot s2 (< 8); code in s1, result a0, then bltz a0
    jal     LOOKUP
    andi    a0, s1, 0xFFFF
    lui     s0, 0x8008
    addiu   s0, s0, 0x4160              ; the original set s0 = font struct before its bltz
    j       0x8002BFE8
    move    a0, v0

.org 0x8002C118                         ; string renderer 1: code at 0x10(sp), result a0, then bltz a0 at C198
    lhu     a0, 0x10(sp)
    jal     LOOKUP
    nop
    j       0x8002C198
    move    a0, v0

.org 0x8002C358                         ; string renderer 2: same shape, bltz a0 at C3D8
    lhu     a0, 0x10(sp)
    jal     LOOKUP
    nop
    j       0x8002C3D8
    move    a0, v0

; --- string renderer 1 width: 0x8002C25C stores text w = cell * strlen (s2) * 2 at +0x18, which the button code
;     centres on (0x8002FF7C, 0x8003009C: x = box x + (box w - text w) / 2). An odd English label ends in a pair
;     whose right half is a space, so it sat 3 px left; trim_hook drops that blank half from the width.
.org 0x8002C218
    jal     trim_hook
    addiu   a3, zero, 0xE               ; replaced: move v1,zero (done in the hook) / addiu a3,zero,0xE

.org FREE
pair_lookup:                            ; v1 = code; return v0 = 0x8000 | n, or -1
    srl     t1, v1, 8
    la      t2, pair_leadidx
    addu    t2, t2, t1
    lbu     t1, 0(t2)
    li      t3, 0xFF
    beq     t1, t3, @@none
    andi    t2, v1, 0xFF
    sltiu   t3, t2, 0x40
    bnez    t3, @@none
    li      t3, 0x7F
    beq     t2, t3, @@none
    sltiu   t3, t2, 0xFD
    beqz    t3, @@none
    addiu   t2, t2, -0x40               ; trail index: 0x40..0x7E -> 0..62, 0x80..0xFC -> 63..187
    sltiu   t3, t2, 0x40
    xori    t3, t3, 1
    subu    t2, t2, t3
    li      t3, 188
    multu   t1, t3
    mflo    t1
    nop
    nop
    addu    t1, t1, t2
    sltiu   t3, t1, PAIR_G * PAIR_G
    beqz    t3, @@none
    nop
    jr      ra
    ori     v0, t1, 0x8000
@@none:
    jr      ra
    li      v0, -1

glyph_hook:                             ; a0 = glyph index
    andi    t0, a0, 0x8000
    bnez    t0, @@pair
    nop
    la      t6, CELLBUF + 5             ; Japanese glyph: the decoder writes 10 of the 12 columns; blank the last
    li      t7, 14                      ; two (byte 5 of each 6-byte row), now that sprites are 12 px wide
@@clr:
    sb      zero, 0(t6)
    addiu   t7, t7, -1
    bnez    t7, @@clr
    addiu   t6, t6, 6
    addiu   sp, sp, -0x30
    j       GLYPH + 8
    lui     v1, 0x8008
@@pair:
    andi    t0, a0, 0x7FFF
    li      t1, PAIR_G
    divu    t0, t1
    mflo    t2                          ; left letter
    mfhi    t3                          ; right letter
    li      t4, 42                      ; bytes per letter
    nop                                 ; mfhi/mflo: two instructions before the next mult/div
    multu   t2, t4
    mflo    t2
    nop
    nop
    multu   t3, t4
    mflo    t3
    la      t5, pair_glyphs
    addu    t2, t2, t5
    addu    t3, t3, t5
    la      t6, CELLBUF
    li      t7, 14
@@row:
    lbu     t0, 0(t2)
    lbu     t1, 1(t2)
    lbu     t4, 2(t2)
    sb      t0, 0(t6)
    sb      t1, 1(t6)
    sb      t4, 2(t6)
    lbu     t0, 0(t3)
    lbu     t1, 1(t3)
    lbu     t4, 2(t3)
    sb      t0, 3(t6)
    sb      t1, 4(t6)
    sb      t4, 5(t6)
    addiu   t2, t2, 3
    addiu   t3, t3, 3
    addiu   t7, t7, -1
    bnez    t7, @@row
    addiu   t6, t6, 6
    jr      ra
    nop

trim_hook:                              ; s2 = strlen (even), s3 = string; s2 -= 1 if the last pair is "x "
    move    t9, ra                      ; returns v1 = 0 (the replaced instruction); s2 is only read for the width
    slti    t0, s2, 2
    bnez    t0, @@done
    addu    t0, s3, s2
    lbu     v1, -2(t0)
    lbu     t0, -1(t0)
    sll     v1, v1, 8
    jal     pair_lookup                 ; uses v1, t1-t3
    or      v1, v1, t0
    bltz    v0, @@done
    andi    v0, v0, 0x7FFF
    li      t0, PAIR_G
    divu    v0, t0
    mfhi    t0
    bnez    t0, @@done
    nop
    addiu   s2, s2, -1
@@done:
    jr      t9
    move    v1, zero

.include "font_data.inc"
font_end:

.if font_end > NAME_COMMIT
    .error "font hook overflows into name_commit (asm/addrs.inc)"
.endif

.include "name.asm"

.if name_end > FREE_END
    .error "name_commit overflows the FREE block"
.endif
.close
