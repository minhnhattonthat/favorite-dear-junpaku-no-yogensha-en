"""batches.wrap: overflowing pages break at a sentence end, and never leave a one-word last page."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import batches as B  # noqa: E402


def pages(s):
    return [p.split("{n}") for p in s.split(B.PAGE)]


def test_fits_unchanged():
    assert B.wrap("Short line.", (44, 3, True)) == "Short line."


def test_sentence_moves_whole():
    text = "One two three four five six seven. " + "Eight nine ten eleven twelve thirteen."
    out = pages(B.wrap(text, (20, 2, True)))
    assert out[0][-1].endswith("seven.")
    assert all(len(p) <= 2 for p in out)


def test_no_lone_short_last_line():
    text = " ".join(["word"] * 25)          # 6 full lines + 1 word at width 20, no sentence end
    out = pages(B.wrap(text, (20, 3, True)))
    assert all(len(p) <= 3 for p in out)
    assert len(out[-1]) >= 2 or B.width(out[-1][0]) >= 20 // 2     # balanced lines: no short lone last line


def test_no_one_word_widow():
    """greedy leaves 'ago.' alone on the last line; the balanced wrap keeps 2 lines and fills the last one"""
    text = " ".join(["word"] * 9) + " ago."       # 9 words fill 44 letters exactly; greedy: "ago." alone
    g = B.greedy(text, 44)
    assert len(g) == 2 and B.width(g[-1]) < B.STUB
    out = B.wrap_lines(text, 44)
    assert len(out) == 2 and B.width(out[-1]) >= B.STUB and all(B.width(x) <= 44 for x in out)
    assert " ".join(out) == text


def test_forced_short_line_kept():
    assert B.wrap_lines("Hey!{n}You.", 44) == ["Hey!", "You."]


def test_every_word_kept():
    text = "Alpha beta. Gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma."
    out = B.wrap(text, (16, 2, True))
    assert out.replace(B.PAGE, " ").replace("{n}", " ").split() == text.split()
