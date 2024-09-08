from dataclasses import asdict, is_dataclass


def merge_dataclasses(dataclass_a, dataclass_b):
    """
    Merge two dataclasses into a new dataclass.
    """
    if (
        is_dataclass(dataclass_a) is False
        and is_dataclass(dataclass_b) is False
    ):
        raise ValueError("Both arguments must be dataclasses.")

    if dataclass_a.__class__ != dataclass_b.__class__:
        raise ValueError("Both dataclasses must be of the same type.")

    data_a = asdict(dataclass_a)
    data_b = asdict(dataclass_b)

    data = {}
    for key in data_a.keys():
        data[key] = data_a[key] if data_a[key] is not None else data_b[key]

    return dataclass_a.__class__(**data)
