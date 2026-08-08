from datetime import datetime, timedelta, date

from models import Match, Prediction, MatchdayXpClaim
from services.level import calculate_level


# =====================================================
# XP REWARD RULES
# =====================================================
# Single source of truth for how much XP each action is
# worth. Keeping these as named constants (instead of
# scattering raw numbers across routes) makes the reward
# table easy to find and tune later.

CORRECT_PREDICTION_XP = 20      # Prediction settled as a win
DAILY_LOGIN_XP = 5              # First login of the (UTC) day
MATCHDAY_COMPLETE_XP = 15       # Predicted every match on a matchday


def add_xp(user, amount: int, db) -> None:
    """
    Adds `amount` XP to `user` and re-derives their level from the
    new total. This is the only place XP should be mutated so the
    level always stays in sync with it.
    """

    user.xp = (user.xp or 0) + amount

    user.level = calculate_level(user.xp)


# =====================================================
# DAILY LOGIN XP
# =====================================================

def award_daily_login_xp(user, db) -> bool:
    """
    Grants DAILY_LOGIN_XP the first time `user` logs in on a given
    UTC calendar day. Safe to call on every login — it's a no-op
    if the bonus was already claimed today.

    Returns True if XP was awarded on this call.
    """

    today = datetime.utcnow().date()

    if user.last_login_date == today:
        return False

    add_xp(user, DAILY_LOGIN_XP, db)

    user.last_login_date = today

    return True


# =====================================================
# MATCHDAY COMPLETION XP
# =====================================================
# A "matchday" is every match sharing the same UTC calendar date.
# The bonus is awarded once per user per matchday, the moment their
# predictions cover every match scheduled that day.

def _day_bounds(day: date):

    start = datetime(day.year, day.month, day.day)

    end = start + timedelta(days=1)

    return start, end


def check_and_award_matchday_bonus(user, db, matchdays) -> int:
    """
    For each date in `matchdays`, checks whether `user` now has a
    prediction on every match scheduled that day. If so (and the
    bonus hasn't already been claimed for that date), awards
    MATCHDAY_COMPLETE_XP once and records the claim.

    Returns the total XP awarded across all the passed-in dates.
    """

    total_awarded = 0

    for day in set(matchdays):

        start, end = _day_bounds(day)

        matches_that_day = db.query(Match).filter(
            Match.match_date >= start,
            Match.match_date < end
        ).all()

        if not matches_that_day:
            continue

        match_ids = {m.id for m in matches_that_day}

        already_claimed = db.query(MatchdayXpClaim).filter(
            MatchdayXpClaim.user_id == user.id,
            MatchdayXpClaim.matchday == day
        ).first()

        if already_claimed:
            continue

        predicted_ids = {
            p.match_id for p in db.query(Prediction).filter(
                Prediction.user_id == user.id,
                Prediction.match_id.in_(match_ids)
            ).all()
        }

        if match_ids.issubset(predicted_ids):

            add_xp(user, MATCHDAY_COMPLETE_XP, db)

            db.add(
                MatchdayXpClaim(
                    user_id=user.id,
                    matchday=day
                )
            )

            total_awarded += MATCHDAY_COMPLETE_XP

    return total_awarded
