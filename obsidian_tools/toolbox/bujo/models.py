import datetime
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Day:

    date: datetime.date
    daily_log_file_path: Path

    @property
    def note_name(self):
        return self.daily_log_file_path.stem

    @property
    def previous_day(self) -> datetime.date:
        return self.date - datetime.timedelta(days=1)

    @property
    def next_day(self) -> datetime.date:
        return self.date + datetime.timedelta(days=1)
    
    @property
    def is_weekend(self) -> bool:
        return self.date.weekday() in (5, 6)
    
    @property
    def is_weekday(self) -> bool:
        return not self.is_weekend


@dataclass
class Week:

    week_number: str
    weekly_log_file_path: Path

    days: list[Day]

    @property
    def start(self) -> datetime.date:
        return self.days[0].date

    @property
    def end(self) -> datetime.date:
        return self.days[-1].date

    @property
    def prev_week_start(self) -> datetime.date:
        return self.start - datetime.timedelta(days=7)

    @property
    def next_week_start(self) -> datetime.date:
        return self.end + datetime.timedelta(days=1)


@dataclass
class Month:

    monthly_log_file_path: Path

    weeks: list[Week]

    @property
    def start_of_month(self):
        return self.weeks[0].start_of_week

    @property
    def end_of_month(self):
        return self.weeks[-1].end_of_week

    @property
    def previous_month(self):
        return (self.start_of_month - datetime.timedelta(days=1)).replace(day=1)

    @property
    def next_month(self):
        return self.end_of_month + datetime.timedelta(days=1)
