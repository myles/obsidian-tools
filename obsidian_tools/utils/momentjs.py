"""
This module provides utilities for working with Moment.js date formats in
Python.

- Obsidian uses Moment.js date formats in its templates, so we have to convert
  them to Python date formats.
"""
import re
import datetime
from typing import Union
from obsidian_tools.utils.humanize import get_ordinal_suffix

MONTH_TOKENS = [
    "MMMM",
    "MMM",
    "MM",
    "Mo",
    "M",
]
QUARTER_TOKENS = [
    "Qo",
    "Q",
]
DAY_OF_MONTH_TOKENS = [
    "DDDD",
    "DDDo",
    "DDD",
    "DD",
    "Do",
    "D",
]

DAY_OF_WEEK_TOKENS = [
    "dddd",
    "ddd",
    "dd",
    "do",
    "d",
]

DAY_OF_WEEK_LOCALE_TOKENS = [
    "e",
]

DAY_OF_WEEK_ISO_TOKENS = [
    "E",
]

WEEK_OF_YEAR_TOKENS = [
    "wo",
    "w"
]

WEEK_OF_YEAR_ISO_TOKENS = [
    "WW",
    "Wo",
    "W",
]

YEAR_TOKENS = [
    "YYYYYY",
    "YYYY",
    "YY",
    "Y",
]

ERA_YEAR_TOKENS = [
    "y",
]

ERA_TOKENS = [
    "NNNNN",
    "NNN",
    "NN",
    "N",
]

WEEK_YEAR_TOKENS = [
    "gggg",
    "gg",
]

WEEK_YEAR_ISO_TOKENS = [
    "GGGG",
    "GG",
]

AM_PM_TOKENS = [
    "A",
    "a",
]

HOUR_TOKENS = [
    "HH",
    "H",
    "hh",
    "h",
    "kk",
    "k",
]

MINUTE_TOKENS = [
    "mm",
    "m",
]

SECOND_TOKENS = [
    "ss",
    "s",
]

FRACTIONAL_SECOND_TOKENS = [
    "SSSSSSS",
    "SSSSSS",
    "SSSSS",
    "SSSS",
    "SSS",
    "SS",
    "S",
]

TIMEZONE_TOKENS = [
    "ZZ",
    "Z",
    "zz",
    "z",
]

UNIX_TIMESTAMP_TOKENS = [
    "X",
]

UNIX_MILLISECOND_TIMESTAMP_TOKENS = [
    "x",
]

TOKENS = [
    *MONTH_TOKENS,
    *QUARTER_TOKENS,
    *DAY_OF_MONTH_TOKENS,
    *DAY_OF_WEEK_TOKENS,
    *DAY_OF_WEEK_LOCALE_TOKENS,
    *DAY_OF_WEEK_ISO_TOKENS,
    *WEEK_OF_YEAR_TOKENS,
    *WEEK_OF_YEAR_ISO_TOKENS,
    *YEAR_TOKENS,
    *ERA_YEAR_TOKENS,
    *ERA_TOKENS,
    *WEEK_YEAR_TOKENS,
    *WEEK_YEAR_ISO_TOKENS,
    *AM_PM_TOKENS,
    *HOUR_TOKENS,
    *MINUTE_TOKENS,
    *SECOND_TOKENS,
    *FRACTIONAL_SECOND_TOKENS,
    *TIMEZONE_TOKENS,
    *UNIX_TIMESTAMP_TOKENS,
    *UNIX_MILLISECOND_TIMESTAMP_TOKENS,
]

RE_FORMAT_CHARACTERS = re.compile(r"(?<!\\)(" + "|".join(TOKENS) + r")")
RE_ESCAPED_CHARACTERS = re.compile(r"\\(.)")


class Formatter:

    def __init__(self, obj: Union[datetime.date, datetime.time, datetime.datetime]):
        self.data = obj

    def format(self, format_str: str) -> str:
        pieces = []
        for i, piece in enumerate(RE_FORMAT_CHARACTERS.split(str(format_str))):
            if i % 2:
                pieces.append(getattr(self, piece)())
            elif piece:
                pieces.append(RE_ESCAPED_CHARACTERS.sub(r"\1", piece))
        return "".join(pieces)

    # Month
    def M(self) -> str:
        """1 2 ... 11 12"""
        return self.data.strftime("%-m")

    def Mo(self) -> str:
        """1st 2nd ... 11th 12th"""
        value = self.M()
        ordinal = get_ordinal_suffix(int(value))
        return f"{value}{ordinal}"

    def MM(self) -> str:
        """01 02 ... 11 12"""
        return self.data.strftime("%m")

    def MMM(self) -> str:
        """Jan Feb ... Nov Dec"""
        return self.data.strftime("%b")

    def MMMM(self) -> str:
        """January February ... November December"""
        return self.data.strftime("%B")

    # Quarter
    def Q(self) -> str:
        """1 2 3 4"""
        return str((self.data.month - 1) // 3 + 1)

    def Qo(self) -> str:
        """1st 2nd 3rd 4th"""
        value = self.Q()
        ordinal = get_ordinal_suffix(int(value))
        return f"{value}{ordinal}"

    # Day of Month
    def D(self) -> str:
        """1 2 ... 30 31"""
        return self.data.strftime("%-d")

    def Do(self) -> str:
        """1st 2nd ... 30th 31st"""
        value = self.D()
        ordinal = get_ordinal_suffix(int(value))
        return f"{value}{ordinal}"

    def DD(self) -> str:
        """01 02 ... 30 31"""
        return self.data.strftime("%d")

    # Day of Year
    def DDD(self) -> str:
        """1 2 ... 364 365"""
        return self.data.strftime("%-j")

    def DDDo(self) -> str:
        """1st 2nd ... 364th 365th"""
        value = self.DDD()
        ordinal = get_ordinal_suffix(int(value))
        return f"{value}{ordinal}"

    def DDDD(self) -> str:
        """001 002 ... 364 365"""
        return self.data.strftime("%j")

    # Day of Week
    def d(self) -> str:
        """0 1 ... 5 6"""
        return self.data.strftime("%w")

    def do(self) -> str:
        """0th 1st ... 5th 6th"""
        value = self.d()
        ordinal = get_ordinal_suffix(int(value))
        return f"{value}{ordinal}"

    def dd(self) -> str:
        """Su Mo ... Fr Sa"""
        return self.data.strftime("%a")

    def ddd(self) -> str:
        """Sun Mon ... Fri Sat"""
        return self.data.strftime("%a")

    def dddd(self) -> str:
        """Sunday Monday ... Friday Saturday"""
        return self.data.strftime("%A")

    # Day of Week (Locale)
    def e(self) -> str:
        raise NotImplementedError

    # Day of Week (ISO)
    def E(self) -> str:
        return str(self.data.isocalendar().weekday)

    # Week of Year
    def w(self) -> str:
        """1 2 ... 52 53"""
        return self.data.strftime("%-U")

    def wo(self) -> str:
        """1st 2nd ... 52nd 53rd"""
        value = self.w()
        ordinal = get_ordinal_suffix(int(value))
        return f"{value}{ordinal}"

    # Week of Year (ISO)
    def W(self) -> str:
        """1 2 ... 52 53"""
        return self.data.strftime("%-V")

    def Wo(self) -> str:
        """1st 2nd ... 52nd 53rd"""
        value = self.W()
        ordinal = get_ordinal_suffix(int(value))
        return f"{value}{ordinal}"

    def WW(self) -> str:
        """01 02 ... 52 53"""
        return self.data.strftime("%V")

    # Year
    def YY(self) -> str:
        """70 71 ... 29 30"""
        return self.data.strftime("%y")

    def YYYY(self) -> str:
        """1970 1971 ... 2029 2030"""
        return self.data.strftime("%Y")

    def YYYYYY(self) -> str:
        """
        -001970 -001971 ... +001907 +001971
        - Note: Expanded Years (Covering the full time value range of
          approximately 273,790 years forward or backward from 01 January, 1970)
        """
        raise NotImplementedError

    def Y(self) -> str:
        """
        1970 1971 ... 9999 +10000 +10001
        - Note: This complies with the ISO 8601 standard for dates past the
          year 9999
        """
        raise NotImplementedError

    # Era Year
    def y(self) -> str:
        """
        1 2 ... 2020 ...
        """
        raise NotImplementedError

    # Era
    def N(self) -> str:
        """
        BC AD
        - Note: Abbr era name
        """
        raise NotImplementedError

    def NN(self) -> str:
        return self.N()

    def NNN(self) -> str:
        return self.N()

    def NNNN(self) -> str:
        """
        Before Christ, Anno Domini
        - Note: Full era name
        """
        raise NotImplementedError

    def NNNNN(self) -> str:
        """
        BC AD
        - Note: Narrow era name
        """
        raise NotImplementedError

    # Week Year
    def gg(self) -> str:
        """70 71 ... 29 30"""
        raise NotImplementedError

    def gggg(self) -> str:
        """1970 1971 ... 2029 2030"""
        raise NotImplementedError

    # Week Year (ISO)
    def GG(self) -> str:
        """70 71 ... 29 30"""
        raise NotImplementedError

    def GGGG(self) -> str:
        """1970 1971 ... 2029 2030"""
        raise NotImplementedError

    # AM/PM
    def A(self) -> str:
        """AM or PM."""
        return self.data.strftime("%p").upper()

    def a(self) -> str:
        """am or pm."""
        return self.A().lower()

    # Hour
    def H(self) -> str:
        """0 1 ... 22 23"""
        return self.data.strftime("%H")

    def HH(self) -> str:
        """00 01 ... 22 23"""
        return self.data.strftime("%H")

    def h(self) -> str:
        """1 2 ... 11 12"""
        return self.data.strftime("%I")

    def hh(self) -> str:
        """01 02 ... 11 12"""
        return self.data.strftime("%I")

    def k(self) -> str:
        """1 2 ... 23 24"""
        raise NotImplementedError

    def kk(self) -> str:
        """01 02 ... 23 24"""
        raise NotImplementedError

    # Minute
    def m(self) -> str:
        """0 1 ... 58 59"""
        return self.data.strftime("%M")

    def mm(self) -> str:
        """00 01 ... 58 59"""
        return self.data.strftime("%M")

    # Second
    def s(self) -> str:
        """0 1 ... 58 59"""
        return self.data.strftime("%S")

    def ss(self) -> str:
        """00 01 ... 58 59"""
        return self.data.strftime("%S")

    # Fractional Second
    def S(self) -> str:
        """0 1 ... 8 9"""
        raise NotImplementedError

    def SS(self) -> str:
        """00 01 ... 98 99"""
        raise NotImplementedError

    def SSS(self) -> str:
        """000 001 ... 998 999"""
        raise NotImplementedError

    def SSSS(self) -> str:
        """0000 0001 ... 9998 9999"""
        raise NotImplementedError

    def SSSSS(self) -> str:
        """00000 00001 ... 99998 99999"""
        raise NotImplementedError

    def SSSSSS(self) -> str:
        """000000 000001 ... 999998 999999"""
        raise NotImplementedError

    def SSSSSSS(self) -> str:
        """0000000 0000001 ... 9999998 9999999"""
        raise NotImplementedError

    def SSSSSSSS(self) -> str:
        """00000000 00000001 ... 99999998 99999999"""
        raise NotImplementedError

    # Timezone
    def z(self) -> str:
        """EST CST ... MST PST"""
        raise NotImplementedError

    def zz(self) -> str:
        return self.z()

    def Z(self) -> str:
        """-07:00 -06:00 ... +06:00 +07:00"""
        raise NotImplementedError

    def ZZ(self) -> str:
        """-0700 -0600 ... +0600 +0700"""
        raise NotImplementedError

    # Unix Timestamp
    def X(self) -> str:
        """1360013296"""
        raise NotImplementedError

    # Unix Millisecond Timestamp
    def x(self) -> str:
        """1360013296123"""
        raise NotImplementedError


def format(value: Union[datetime.date, datetime.time, datetime.datetime], format_str: str) -> str:
    return Formatter(value).format(format_str)
