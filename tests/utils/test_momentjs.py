from obsidian_tools.utils import momentjs
import datetime


def test_formatter__format():
    date = datetime.date(2021, 1, 1)
    format_str = "YYYY-MM-DD"
    result = momentjs.format(date, format_str)
    assert result == "2021-01-01"


def test_formatter__format__escaped():
    date = datetime.date(2021, 1, 1)
    format_str = "YYYYMMDD [\\Y\\Y\\Y\\Y\\M\\M\\D\\D]"
    result = momentjs.format(date, format_str)
    assert result == "20210101 [YYYYMMDD]"


def test_formatter__wo():
    date = datetime.date(2021, 1, 1)
    format_str = "wo"
    result = momentjs.format(date, format_str)
    assert result == "0th"


def test_formatter__w():
    date = datetime.date(2021, 1, 1)
    format_str = "w"
    result = momentjs.format(date, format_str)
    assert result == "0"


def test_formatter__W():
    date = datetime.date(2021, 1, 1)
    format_str = "W"
    result = momentjs.format(date, format_str)
    assert result == "53"


def test_formatter__Wo():
    date = datetime.date(2021, 1, 1)
    format_str = "Wo"
    result = momentjs.format(date, format_str)
    assert result == "53rd"


def test_formatter__WW():
    date = datetime.date(2021, 1, 1)
    format_str = "WW"
    result = momentjs.format(date, format_str)
    assert result == "53"


def test_format__date():
    date = datetime.date(2021, 1, 1)
    format_str = "YYYY-MM-DD"
    result = momentjs.format(date, format_str)
    assert result == "2021-01-01"


def test_format__time():
    time = datetime.time(12, 34, 56)
    format_str = "HH:mm:ss"
    result = momentjs.format(time, format_str)
    assert result == "12:34:56"


def test_format__datetime():
    dt = datetime.datetime(2021, 1, 1, 12, 34, 56)
    format_str = "YYYY-MM-DD HH:mm:ss"
    result = momentjs.format(dt, format_str)
    assert result == "2021-01-01 12:34:56"
