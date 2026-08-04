from datetime import datetime, timedelta, timezone
from typing import Iterable

from sqlalchemy.orm import Session

from models import Match


def to_naive_utc(value: datetime) -> datetime:
    """
    Normalizes any datetime we receive into naive UTC, which is the
    convention the rest of the backend assumes (sync_match_statuses
    compares against datetime.utcnow()).

    - If the value already carries timezone info (e.g. the frontend
      sent a proper ISO string with an offset/'Z'), convert it to
      UTC and drop the tzinfo.
    - If it's naive (no tzinfo), we trust it's already UTC — this
      keeps old data / any caller that still sends naive strings
      working exactly as before.
    """

    if value.tzinfo is not None:

        value = value.astimezone(timezone.utc).replace(tzinfo=None)

    return value


def get_match_end(match: Match) -> datetime:
    """
    The moment a match should stop being considered LIVE — kickoff
    (match_date) plus its duration (defaults to 90 minutes for
    matches created before duration_minutes existed).
    """

    duration = match.duration_minutes or 90

    return match.match_date + timedelta(minutes=duration)


def sync_match_statuses(db: Session, matches: Iterable[Match]) -> None:
    """
    Auto-flips a match from UPCOMING -> LIVE the moment its kickoff
    time (match_date) is reached, so the homepage / admin panel
    always reflect real kickoff time without needing an admin to
    manually toggle anything.

    We deliberately do NOT auto-flip LIVE -> FINISHED here. Turning
    a match FINISHED still requires an admin to enter the final
    score via /results/{match_id}, since that's what settles
    predictions and awards points. Once a match's live window
    (kickoff -> kickoff + duration) has passed, the homepage simply
    stops *displaying* it as live/upcoming — that's handled on the
    read side (frontend + /matches/live), independent of this
    status field.
    """

    now = datetime.utcnow()

    changed = False

    for match in matches:

        if match.status == "UPCOMING" and match.match_date <= now:

            match.status = "LIVE"

            changed = True

    if changed:

        db.commit()
