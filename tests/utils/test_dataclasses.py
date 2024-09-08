from dataclasses import dataclass
from typing import Union

from obsidian_tools.utils import dataclasses


@dataclass
class ExampleDataClass:
    a: Union[str, None]
    b: Union[str, None]
    c: Union[str, None]


@dataclass
class OtherExampleDataClass: ...


def test_merge_dataclasses():
    a = ExampleDataClass(a="a", b="b", c=None)
    b = ExampleDataClass(a=None, b="dont-merge", c="c")

    merged_dataclass = dataclasses.merge_dataclasses(a, b)

    assert merged_dataclass.a == "a"
    assert merged_dataclass.b == "b"


def test_merge_dataclasses__not_dataclasses():
    try:
        dataclasses.merge_dataclasses("a", "b")
    except ValueError as e:
        assert str(e) == "Both arguments must be dataclasses."


def test_merge_dataclasses__different_types():
    a = ExampleDataClass(a="a", b="b", c=None)
    b = OtherExampleDataClass()

    try:
        dataclasses.merge_dataclasses(a, b)
    except ValueError as e:
        assert str(e) == "Both dataclasses must be of the same type."
