import pytest

from obsidian_tools.utils import humanize


@pytest.mark.parametrize(
    "words, separator, ending_separator, series_separator, expected_result",
    (
        (
            ["a"],
            ", ",
            " and ",
            True,
            "a",
        ),
        (
            ["a", "b"],
            ", ",
            " and ",
            True,
            "a and b",
        ),
        (
            ["a", "b", "c"],
            ", ",
            " and ",
            True,
            "a, b, and c",
        ),
        (
            ["a", "b", "c"],
            ", ",
            " and ",
            False,
            "a, b and c",
        ),
        (
            ["a", "b"],
            ", ",
            None,
            False,
            "a, b",
        ),
        (
            ["a", "b", "c"],
            ", ",
            None,
            False,
            "a, b, c",
        ),
    ),
)
def test_list_join(
    words, separator, ending_separator, series_separator, expected_result
):
    result = humanize.list_join(
        words,
        separator=separator,
        ending_separator=ending_separator,
        series_separator=series_separator,
    )
    assert result == expected_result


def test_and_join():
    result = humanize.and_join(["a"])
    assert result == "a"

    result = humanize.and_join(["a", "b"])
    assert result == "a and b"

    result = humanize.and_join(["a", "b", "c"])
    assert result == "a, b, and c"


def test_or_join():
    result = humanize.or_join(["a"])
    assert result == "a"

    result = humanize.or_join(["a", "b"])
    assert result == "a or b"

    result = humanize.or_join(["a", "b", "c"])
    assert result == "a, b, or c"
