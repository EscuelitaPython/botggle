
from botggle.game import SCORES_TABLE


def get_user_round_result(result_words):
    """Arma la cadena de resultad de ronda para un usuario."""
    words_by_len = {}

    for word in result_words.valid:
        score = SCORES_TABLE[len(word)]
        wordslist = words_by_len.setdefault(score, [])
        wordslist.append(word)

    if words_by_len:
        info_valid = "; ".join(
            f"[{key}] {', '.join(sorted(value))}" for key, value in sorted(words_by_len.items()))
    else:
        info_valid = "---"
    r_valid = info_valid

    if result_words.repeated:
        info_repeated = ", ".join(sorted(result_words.repeated))
    else:
        info_repeated = "---"
    r_repeated = f"REPES: {info_repeated}"

    if result_words.not_in_language:
        info_nolang = ", ".join(sorted(result_words.not_in_language))
    else:
        info_nolang = "---"
    r_nolang = f"NO-DICC: {info_nolang}"

    r_noboard = "NO-TABLERO: ---"

    return " | ".join((r_valid, r_repeated, r_nolang, r_noboard))
