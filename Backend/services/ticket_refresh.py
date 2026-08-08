from datetime import datetime, timedelta

from models import Profile, TicketHistory


# Flat number of tickets granted on every daily refresh, once the
# user's initial free-ticket balance has been fully depleted.
DAILY_TICKET_AMOUNT = 2


def _next_midnight_utc(after: datetime) -> datetime:
    """
    Returns the next UTC midnight (12:00 AM) strictly after `after`.
    """

    next_day = (after + timedelta(days=1)).date()

    return datetime(
        next_day.year,
        next_day.month,
        next_day.day
    )


def sync_daily_tickets(user: Profile, db) -> None:
    """
    Lazily applies the daily ticket-refresh cycle for `user`.

    Rules:
    - Every new user starts with their initial free ticket balance
      (5 by default, see Profile.tickets) and is NOT on the daily
      cycle yet — next_ticket_reset stays NULL.
    - The daily cycle activates the very first time a user's
      tickets fully deplete (hit 0). From that point on, every day
      at 12:00 AM (UTC midnight) their balance is snapped to a flat
      2 tickets — it is never stacked on top of leftovers, and it
      doesn't matter whether the previous day's tickets were used
      or not.
    - If a user is away for multiple days, catching up still just
      leaves them with 2 tickets (not 2 x days-missed) — the reset
      is a flat assignment, not an accumulation.
    - Admins are exempt from the daily cycle.

    Called lazily (no cron/scheduler in this codebase) from the
    request paths that load a user's ticket balance, so the refresh
    is applied transparently on the next request after a reset
    boundary is crossed.
    """

    if user is None or user.role == "ADMIN":
        return

    now = datetime.utcnow()

    # -----------------------------------------
    # ACTIVATE the daily cycle the first time
    # tickets hit zero.
    # -----------------------------------------
    if (
        user.tickets is not None
        and user.tickets <= 0
        and user.next_ticket_reset is None
    ):

        user.next_ticket_reset = _next_midnight_utc(now)

        db.commit()
        db.refresh(user)

        return

    # -----------------------------------------
    # APPLY a refresh once a reset boundary has
    # been crossed.
    # -----------------------------------------
    if (
        user.next_ticket_reset is not None
        and now >= user.next_ticket_reset
    ):

        user.tickets = DAILY_TICKET_AMOUNT

        # Regardless of how many midnights were missed while the
        # user was away, the next reset is simply the next midnight
        # after now — the balance itself never stacks.
        user.next_ticket_reset = _next_midnight_utc(now)

        db.add(
            TicketHistory(
                user_id=user.id,
                amount=DAILY_TICKET_AMOUNT,
                action="DAILY_REFRESH"
            )
        )

        db.commit()
        db.refresh(user)
