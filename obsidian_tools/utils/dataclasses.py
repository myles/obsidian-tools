from dataclasses import asdict, is_dataclass


def is_iterable(obj) -> bool:
    """
    Is the object iterable?
    """
    if isinstance(obj, str):
        return False

    try:
        iter(obj)
    except TypeError:
        return False

    return True


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

    dataclass = dataclass_a.__class__

    data_a = asdict(dataclass_a)
    data_b = asdict(dataclass_b)

    data = {}
    for key in data_a.keys():
        if is_dataclass(dataclass.__annotations__[key]):
            data[key] = merge_dataclasses(
                getattr(dataclass_a, key),
                getattr(dataclass_b, key),
            )
        elif is_iterable(data_a[key]) or is_iterable(data_b[key]):
            list_a = getattr(dataclass_a, key) or []
            list_b = getattr(dataclass_b, key) or []
            data[key] = list(set(list_a + list_b))
        else:
            data[key] = data_a[key] or data_b[key]

    return dataclass_a.__class__(**data)
