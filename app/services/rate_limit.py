from datetime import UTC, date, datetime

from fastapi import HTTPException

DAILY_LIMIT = 100

_count = 0
_count_date: date = datetime.now(UTC).date()


def check_and_increment() -> None:
    """Raise 429 once DAILY_LIMIT generations have been used today (UTC)."""
    global _count, _count_date

    today = datetime.now(UTC).date()
    if today != _count_date:
        _count = 0
        _count_date = today

    if _count >= DAILY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Daily generation limit reached ({DAILY_LIMIT}/day). Try again tomorrow.",
        )

    _count += 1
