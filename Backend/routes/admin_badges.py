from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Badge,
    UserBadge,
    Profile
)

from dependencies import require_admin

from services.seed import seed_badges

from services.badges import sync_badges

from pydantic import BaseModel



router = APIRouter(
    prefix="/admin/badges",
    tags=["Admin Badges"]
)



VALID_RARITIES = [
    "Common",
    "Uncommon",
    "Rare",
    "Epic",
    "Legendary"
]



# ================================
# SCHEMAS
# ================================


class BadgeCreate(BaseModel):

    name: str

    description: str | None = None

    icon: str | None = None

    rarity: str | None = "Common"




class BadgeUpdate(BaseModel):

    name: str | None = None

    description: str | None = None

    icon: str | None = None

    rarity: str | None = None




# ================================
# RESEED DEFAULT CATALOG
# ================================
# Forces the default badge catalog (First Prediction, First Win,
# Hot Streak, etc.) to be (re)inserted right now, without waiting
# for a server restart. Useful right after pointing the backend
# at a new/empty Supabase database.


@router.post("/reseed")
def reseed_default_badges(

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):

    result = seed_badges(db)

    return {

        "message": "Default badge catalog synced",

        **result

    }




# ================================
# RECALCULATE FOR ALL USERS
# ================================
# Rank badges (Bronze/Silver/Gold/Elite Predictor) and milestone
# badges (Legend, Prediction Master) only ever get (re)checked
# live, from the one code path where a user's points change (a
# winning prediction). Any user whose points/wins already
# qualified before that — seeded accounts, points set some other
# way, or anyone who simply hasn't won since the badge was added —
# won't have it until this runs. GET /players/{username} does this
# automatically per-user on profile load; this endpoint sweeps
# every user in one go, e.g. right after deploying a badges change.


@router.post("/recalculate")
def recalculate_all_badges(

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):

    users = db.query(Profile).all()

    for user in users:
        sync_badges(db, user)

    db.commit()

    return {

        "message": "Rank and milestone badges recalculated for all users",

        "users_checked": len(users)

    }




# ================================
# GET ALL BADGES
# ================================


@router.get("")
def get_badges(

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    badges = db.query(Badge).order_by(
        Badge.created_at
    ).all()



    result = []

    for badge in badges:

        earned_count = db.query(UserBadge).filter(
            UserBadge.badge_id == badge.id
        ).count()

        result.append({

            "id": str(badge.id),

            "name": badge.name,

            "description": badge.description,

            "icon": badge.icon,

            "rarity": badge.rarity or "Common",

            "earned_count": earned_count,

            "created_at": badge.created_at

        })


    return result




# ================================
# CREATE BADGE
# ================================


@router.post("")
def create_badge(

    data: BadgeCreate,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    existing = db.query(Badge).filter(
        Badge.name == data.name
    ).first()


    if existing:

        raise HTTPException(
            400,
            "A badge with this name already exists"
        )



    rarity = data.rarity or "Common"

    if rarity not in VALID_RARITIES:

        raise HTTPException(
            400,
            f"Rarity must be one of: {', '.join(VALID_RARITIES)}"
        )



    badge = Badge(

        name=data.name,

        description=data.description,

        icon=data.icon,

        rarity=rarity

    )


    db.add(badge)

    db.commit()

    db.refresh(badge)



    return {

        "message": "Badge created successfully",

        "badge": {

            "id": str(badge.id),

            "name": badge.name,

            "description": badge.description,

            "icon": badge.icon,

            "rarity": badge.rarity

        }

    }




# ================================
# UPDATE BADGE
# ================================


@router.put("/{badge_id}")
def update_badge(

    badge_id: str,

    data: BadgeUpdate,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    badge = db.query(Badge).filter(
        Badge.id == badge_id
    ).first()


    if not badge:

        raise HTTPException(
            404,
            "Badge not found"
        )



    updates = data.dict(exclude_unset=True)


    if "rarity" in updates and updates["rarity"] not in VALID_RARITIES:

        raise HTTPException(
            400,
            f"Rarity must be one of: {', '.join(VALID_RARITIES)}"
        )


    for key, value in updates.items():

        setattr(badge, key, value)


    db.commit()

    db.refresh(badge)



    return {

        "message": "Badge updated successfully",

        "badge": {

            "id": str(badge.id),

            "name": badge.name,

            "description": badge.description,

            "icon": badge.icon,

            "rarity": badge.rarity

        }

    }




# ================================
# DELETE BADGE
# ================================


@router.delete("/{badge_id}")
def delete_badge(

    badge_id: str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    badge = db.query(Badge).filter(
        Badge.id == badge_id
    ).first()


    if not badge:

        raise HTTPException(
            404,
            "Badge not found"
        )


    db.query(UserBadge).filter(
        UserBadge.badge_id == badge.id
    ).delete()


    db.delete(badge)

    db.commit()



    return {

        "message": "Badge deleted successfully"

    }
