from models import Badge, UserBadge
from services.ranks import get_rank


def award_badge(db, user, badge_name):
    """
    Awards `badge_name` to `user` if it exists and they don't
    already have it. Safe to call repeatedly — duplicates are
    skipped. Caller is responsible for db.commit().
    """

    badge = db.query(Badge).filter(
        Badge.name == badge_name
    ).first()

    if not badge:
        return

    exists = db.query(UserBadge).filter(
        UserBadge.user_id == user.id,
        UserBadge.badge_id == badge.id
    ).first()

    if exists:
        return

    db.add(
        UserBadge(
            user_id=user.id,
            badge_id=badge.id
        )
    )


# ==========================================
# RANK BADGES
# ==========================================
# Checks the user's CURRENT points against the rank ladder and
# awards every rank badge they've earned so far. Call this any
# time user.points changes so badges unlock the moment the
# criteria is met.

def check_rank_badges(db, user):

    rank = get_rank(user.points or 0)

    reached = {
        "BRONZE": ["BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "LEGEND"],
        "SILVER": ["SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "LEGEND"],
        "GOLD": ["GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "LEGEND"],
        "PLATINUM": ["PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "LEGEND"],
    }

    if rank in reached["BRONZE"]:
        award_badge(db, user, "Bronze Predictor")

    if rank in reached["SILVER"]:
        award_badge(db, user, "Silver Predictor")

    if rank in reached["GOLD"]:
        award_badge(db, user, "Gold Predictor")

    # "Elite Predictor" pre-dates the current rank ladder (which no
    # longer has an "Elite" tier). It now unlocks alongside Platinum,
    # the tier that replaced it as the step above Gold.
    if rank in reached["PLATINUM"]:
        award_badge(db, user, "Elite Predictor")


# ==========================================
# MILESTONE BADGES
# ==========================================
# Checks point / streak / win-count milestones unrelated to rank.

def check_milestone_badges(db, user):

    if (user.points or 0) >= 1000:
        award_badge(db, user, "Legend")

    if (user.wins or 0) >= 100:
        award_badge(db, user, "Prediction Master")

    # NOTE: "Hot Streak" is awarded directly in routes/results.py
    # right after a winning ticket bumps current_streak, since
    # that's the single place the streak counter actually changes.


# ==========================================
# FULL SYNC
# ==========================================
# Re-runs every stats-derived badge check (rank ladder + milestones)
# against a user's CURRENT points/wins. check_rank_badges and
# check_milestone_badges only ever get called from the one code
# path where points change (a winning prediction in results.py),
# so any user who already qualified before that point — seeded
# accounts, points adjusted some other way, or simply anyone who
# hasn't won since the badge existed — would otherwise never
# receive it. Calling this whenever a profile is read (see
# routes/players.py) makes badge state self-healing for every
# user, regardless of how or when their stats got there. Safe and
# cheap to call repeatedly — award_badge() no-ops on duplicates.

def sync_badges(db, user):

    check_rank_badges(db, user)
    check_milestone_badges(db, user)
