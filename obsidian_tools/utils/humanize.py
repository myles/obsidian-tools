from typing import Final, List, Optional

DEFAULT_SEPARATOR: Final = ", "
AND_ENDING_SEPARATOR: Final = " and "
OR_ENDING_SEPARATOR: Final = " or "


def list_join(
    words: List[str],
    *,
    separator: str,
    ending_separator: Optional[str] = None,
    series_separator: bool = True,
) -> str:
    """
    Convert a list of strings into a natural language enumeration.
    """
    if not words:
        return ""

    if len(words) == 1:
        return words[0]

    if ending_separator is None:
        ending_separator = separator
    elif len(words) > 2 and series_separator is True:
        ending_separator = f"{separator.rstrip()} {ending_separator.lstrip()}"

    last_word = words.pop(-1)

    return f"{separator.join(words)}{ending_separator}{last_word}"


def and_join(words: List[str]) -> str:
    """
    Convert a list of strings into a natural language enumeration separated by
    commas and "and".
    """
    return list_join(
        words,
        separator=DEFAULT_SEPARATOR,
        ending_separator=AND_ENDING_SEPARATOR,
    )


def or_join(words: List[str]) -> str:
    """
    Convert a list of strings into a natural language enumeration separated by
    commas and "or".
    """
    return list_join(
        words,
        separator=DEFAULT_SEPARATOR,
        ending_separator=OR_ENDING_SEPARATOR,
    )


def get_ordinal_suffix(value: int) -> str:
    """
    Get the ordinal suffix.
    """
    if 10 <= value % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")

    return suffix
