from __future__ import annotations

from datetime import datetime, timedelta


def month_cells(month: datetime) -> list[datetime | None]:
    first_day = datetime(month.year, month.month, 1)
    days: list[datetime | None] = [None for _ in range(first_day.weekday())]

    current = first_day
    while current.month == month.month:
        days.append(current)
        current += timedelta(days=1)

    while len(days) < 42:
        days.append(None)
    return days


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
