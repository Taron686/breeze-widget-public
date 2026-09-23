from __future__ import annotations

from calendar import monthrange
from datetime import datetime


def month_cells(month: datetime) -> list[datetime | None]:
    first_day = datetime(month.year, month.month, 1)
    start = first_day.toordinal() - first_day.weekday()
    count = ((first_day.weekday() + monthrange(month.year, month.month)[1] + 6) // 7) * 7
    # Complete Monday-first weeks, including selectable neighbouring dates.
    # Only cells outside Python's supported date range remain empty.
    days = [datetime.fromordinal(day) if 1 <= day <= datetime.max.toordinal() else None
            for day in range(start, start + count)]
    return days + [None] * (42 - count)


def activity_for_day(
    activities: dict[str, dict[int, str]],
    month: datetime,
    day: datetime,
) -> str:
    month_key = month.strftime("%m-%Y")
    return activities.get(month_key, {}).get(day.day) or ""


def week_numbers_for_cells(cells: list[datetime | None]) -> list[str]:
    week_numbers: list[str] = []
    for row in range(6):
        week_numbers.append(_week_number_for_row(cells[row * 7 : row * 7 + 7]))
    return week_numbers


def _week_number_for_row(row: list[datetime | None]) -> str:
    for day in row:
        if day is not None:
            return str(day.date().isocalendar()[1])
    return ""
