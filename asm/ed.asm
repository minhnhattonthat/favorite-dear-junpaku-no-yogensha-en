; ed.asm: endings overlay (FD2BN ed.bin, loaded at 0x8009B4B0). armips, run by tools/build.py (patch_ed):
;   armips asm/ed.asm -strequ ED_IN <in> -strequ ED_OUT <out>
; The ending narration (0x8009CC50) loads the .end file from a table at 0x8009E42C: 8 words per hero
; (fe cl lo ro ei la ce), words 2/4/6 = LKF index of grade 1/2/3's .end, words 3/5/7 = the number of lines it
; draws (only that many CRLF lines are read; docs/re/text.md §.end files). ceed3.end's text runs to line 38 but
; its count is 34, so the original drops the closing "私の愛する人々と世界へ……" that every other ending shows
; (decision D-ceed3 in docs/decisions.md). 38 is within what the other endings draw (46-47).

.psx
.open ED_IN, ED_OUT, 0x8009B4B0

.org 0x8009E42C + 6 * 32 + 7 * 4        ; Cecia (hero 6), grade 3 line count
.word 38

.close
