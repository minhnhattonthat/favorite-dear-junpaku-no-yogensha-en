# Translator brief

Read first: `glossary.md` (rulings, style rules, term tables; read it in parts of ~60 lines), the voice notes below.

Input: `trans/batches/bNNN.tsv`, columns `id kind speaker jp` (read in parts of ~25 lines: batches are ~12 KB).
- `kind`: `wrapWxL` = dialogue that `batches.py merge` wraps at W letters, L lines per page (it adds
  `{wait}{clear}` pages when a page runs over); write flowing text, `{n}` only where a break must fall.
  `name` = speaker / unit name, 12 letters max. Anything else (`ptrx1`, `luix1`, `table`, `fixed`, `text`): code
  strings, keep the layout and codes exactly; length is fitted in phase 7.
- Keep every code other than `{n}` in order (`{wait}{clear}`, `{A5}`...). Keep ＄＄＄＄＄＄ (the player's name).
- Rows with the same JP appear once; merge copies the English to every copy.

Output: `trans/en/bNNN.tsv`, header `id<TAB>en`, every batch id once, plain ASCII from the font (no # $ < > @ [ \ ] ^ _ `
{ | } outside codes), `-` to leave a row Japanese (report why). Written in parts under `trans/parts/` and joined.

Check: `python -X utf8 tools/batches.py check bNNN` until it prints OK; then `python -X utf8 tools/batches.py merge`.

Voices: every recurring speaker's JP markers -> EN devices, with paired examples, are in `docs/style-reference.md`
(binding; read it in parts). A neutral line where the JP carries a voice is Important in review. Short form:
- Rosa (ローザ): formal, composed, complete sentences, no contractions in narration-style reports.
- Florinda (フロリンダ): childish and bubbly, calls herself "Florin" in the third person, stretched vowels
  (わかりましたぁ "Okaaay!"), ですぅ as exclamation marks and "super", "kinda".
- Shelly (シェリー): cheerful and polite, light contractions.

Quality bar (past mistakes in this series): names off by a letter; honorifics dropped; the angel gendered; jokes
flattened; quirks (ですぅ, っス, のじゃ) normalised into neutral English; "1th" after a number variable.

Report at the end: `NEW TERM: jp -> en`, `UNSURE: id - note`, `CUT: id - what was dropped`.
