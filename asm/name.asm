; name.asm: included by font.asm (EXE FREE block). The name entry (pro.bin) commits the chosen name with
; memcpy(0x8007F480, entry + 0x612, 12): a full-width SJIS string from the kana grid. asm/pro.asm points that call
; here instead, so full-width Latin letters, digits, space, ! and ? are stored as English pair codes (the dialogue
; font draws full-width Latin as wide Japanese-cell letters). Other characters (kana) are kept; a letter run of odd
; length gets a trailing space (pair glyphs fill whole cells). Python model and test: font_en.name_to_pairs.
; Needs (-equ from build.patch_exe): PAIR_G, CH_SPACE, CH_EXCL, CH_QUES, CH_0, CH_UA, CH_LA.

.org NAME_COMMIT
name_to_pairs:                          ; (armips equs are case-insensitive: a label can't be called NAME_COMMIT)
                                        ; a0 = dst (12 bytes), a1 = src (SJIS, 12 bytes or up to a NUL)
    move    t8, ra
    addiu   t0, a1, 12                  ; src end
    addiu   t9, a0, 12                  ; dst end
    li      t7, -1                      ; pending letter (-1: none)
@@next:
    sltu    t3, a1, t0
    beqz    t3, @@end
    nop
    lbu     t4, 0(a1)
    lbu     t5, 1(a1)
    beqz    t4, @@end
    sll     t4, t4, 8
    or      t4, t4, t5                  ; t4 = SJIS code
    addiu   a1, a1, 2
    ori     t3, zero, 0x8260            ; Ａ-Ｚ (subtract through a register: -0x8260 is no 16-bit immediate)
    subu    t3, t4, t3
    sltiu   t5, t3, 26
    bnez    t5, @@letter
    addiu   t6, t3, CH_UA
    ori     t3, zero, 0x8281            ; ａ-ｚ
    subu    t3, t4, t3
    sltiu   t5, t3, 26
    bnez    t5, @@letter
    addiu   t6, t3, CH_LA
    ori     t3, zero, 0x824F            ; ０-９
    subu    t3, t4, t3
    sltiu   t5, t3, 10
    bnez    t5, @@letter
    addiu   t6, t3, CH_0
    ori     t3, zero, 0x8140            ; full-width space
    beq     t4, t3, @@letter
    addiu   t6, zero, CH_SPACE
    ori     t3, zero, 0x8148            ; ？
    beq     t4, t3, @@letter
    addiu   t6, zero, CH_QUES
    ori     t3, zero, 0x8149            ; ！
    beq     t4, t3, @@letter
    addiu   t6, zero, CH_EXCL
    bltz    t7, @@copy                  ; another character: close the pending letter with a space, copy the code
    nop
    move    a2, t7
    jal     @@emit
    addiu   a3, zero, CH_SPACE
    addiu   t7, zero, -1
@@copy:
    srl     t3, t4, 8
    sb      t3, 0(a0)
    sb      t4, 1(a0)
    b       @@next
    addiu   a0, a0, 2
@@letter:
    bgez    t7, @@pair
    nop
    b       @@next
    move    t7, t6
@@pair:
    move    a2, t7
    jal     @@emit
    move    a3, t6
    b       @@next
    addiu   t7, zero, -1
@@end:
    bltz    t7, @@pad
    nop
    move    a2, t7
    jal     @@emit
    addiu   a3, zero, CH_SPACE
@@pad:
    sltu    t3, a0, t9
    beqz    t3, @@ret
    nop
    sb      zero, 0(a0)
    b       @@pad
    addiu   a0, a0, 1
@@ret:
    jr      t8
    nop

@@emit:                                 ; pair (a2, a3) -> 2 bytes at a0, a0 += 2 (tools/font_en.pair_code)
    addiu   v0, zero, PAIR_G
    multu   a2, v0
    mflo    v0
    addu    v0, v0, a3                  ; n
    addiu   v1, zero, 188
    divu    v0, v1
    mflo    t1                          ; lead index
    mfhi    t2                          ; trail index
    la      v1, pair_leads
    addu    v1, v1, t1
    lbu     v1, 0(v1)
    sltiu   t1, t2, 63                  ; trails skip 0x7F
    xori    t1, t1, 1
    addu    t2, t2, t1
    addiu   t2, t2, 0x40
    sb      v1, 0(a0)
    sb      t2, 1(a0)
    jr      ra
    addiu   a0, a0, 2
name_end:
