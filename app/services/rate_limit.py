from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

WINDOW = timedelta(hours=12)
LIMIT = 50

_calls: list[datetime] = []


def check_and_increment() -> None:
    """Raise 429 once LIMIT generations have been used in the last WINDOW."""
    global _calls
    now = datetime.now(UTC)

    cutoff = now - WINDOW
    _calls = [t for t in _calls if t > cutoff]

    if len(_calls) >= LIMIT:
        raise HTTPException(
                    status_code=429,
                    detail=f"Period generation limit reached ({LIMIT}/12 hours). Try again later.",
                )

    _calls.append(now)
