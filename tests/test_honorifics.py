"""D1/D9 honorific lint (tools/honorifics.py) and the propose step's rewrites."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import honorifics as H  # noqa: E402

NM = {"ラファエル": "Raphael", "レイラ": "Leyla", "ヴィグリード": "Vigrid", "フェイン": "Fein"}


def test_missing_flags_lord_title():
    assert H.missing("ラファエル様！", "Lord Raphael!", NM)
    assert not H.missing("ラファエル様！", "Raphael-sama!", NM)


def test_full_name_and_placeholder():
    assert H.missing("レイラ・ヴィグリード様が", "Leyla Vigrid has", NM)
    assert not H.missing("レイラ・ヴィグリード様が", "Leyla Vigrid-sama has", NM)
    assert H.missing("＜勇者名＞様が", "＜勇者名＞ has", NM)


def test_unknown_names_and_address_nouns_pass():
    assert not H.missing("天使様、お父様", "Angel, Father", NM)


def test_propose_drops_title():
    assert H.propose_row("ラファエル様、", "Lord Raphael,", NM) == ("auto", "Raphael-sama,")
    # the JP also uses the bare name and the EN has no title to convert: left for a hand fix
    assert H.propose_row("フェイン様……フェイン", "Fein... Fein", NM) == ("mixed", "?")
