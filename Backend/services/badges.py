from models import Badge, UserBadge

def award_badge(db, user, badge_name):

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