from dataclasses import dataclass, field
from typing import List, Union

from obsidian_tools.utils import dataclasses


@dataclass
class ExampleDataClass:
    a: Union[str, None]
    b: Union[str, None]
    c: Union[str, None]

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b and self.c == other.c

    def __hash__(self):
        return hash((self.a, self.b, self.c))


@dataclass
class OtherExampleDataClass: ...


@dataclass
class ExampleDataClassTwo:
    a: ExampleDataClass
    b: List[ExampleDataClass] = field(default_factory=list)


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


def test_merge_dataclasses__has_dataclass():
    a = ExampleDataClass(a="a", b="b", c=None)
    b = ExampleDataClass(a=None, b="dont-merge", c="c")

    aa = ExampleDataClassTwo(a=a)
    bb = ExampleDataClassTwo(a=b)

    merged_dataclass = dataclasses.merge_dataclasses(bb, aa)
    assert merged_dataclass.a.a == "a"


def test_merge_dataclasses__list_dataclass():
    a = ExampleDataClass(a="a1", b="a2", c="a3")
    b = ExampleDataClass(a="b1", b="b2", c="b3")

    aa = ExampleDataClassTwo(a=a, b=[a])
    bb = ExampleDataClassTwo(a=b, b=[b])

    merged_dataclass = dataclasses.merge_dataclasses(bb, aa)
    assert len(merged_dataclass.b) == 2
    assert a in merged_dataclass.b
    assert b in merged_dataclass.b
