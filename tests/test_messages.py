"""Tests for the messages module."""

from botggle.game import ResultWords
from botggle.messages import get_user_round_result


def test_case_1():
    result = get_user_round_result(
        ResultWords(
            valid={'ene', 'cela'},
            repeated={'lia', 'des'},
            not_in_language={'cene', 'lea', 'lee', 'caes', 'cae'},
            not_in_board=set(),
        )
    )
    assert result == (
        "[1] ene; [2] cela | REPES: des, lia | "
        "NO-DICC: cae, caes, cene, lea, lee | NO-TABLERO: ---")


def test_case_2():
    result = get_user_round_result(
        ResultWords(
            valid={"junta", 'ene', 'cela', "for"},
            repeated=set(),
            not_in_language=set(),
            not_in_board=set(),
        )
    )
    assert result == (
        "[1] ene, for; [2] cela; [4] junta | REPES: --- | NO-DICC: --- | NO-TABLERO: ---")


def test_case_3():
    result = get_user_round_result(
        ResultWords(
            valid={"juna", 'ene', 'cela', "for"},
            repeated=set(),
            not_in_language=set(),
            not_in_board=set(),
        )
    )
    assert result == (
        "[1] ene, for; [2] cela, juna | REPES: --- | NO-DICC: --- | NO-TABLERO: ---")
