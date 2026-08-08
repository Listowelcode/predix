from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from database import get_db

from models import Profile

from typing import List

from services.ranks import get_rank_info



router = APIRouter(
    prefix="/leaderboard",
    tags=["Leaderboard"]
)



# =====================================
# GLOBAL LEADERBOARD
# =====================================


@router.get("")
def get_leaderboard(

    db: Session = Depends(get_db)

):


    users = db.query(Profile).order_by(

        Profile.points.desc()

    ).limit(100).all()



    leaderboard = []



    for index, user in enumerate(users, start=1):


        # Points-based tier (Bronze -> Legend), same table used on
        # the profile page — a user's rank icon should always match
        # regardless of where their position falls in the list.
        rank_tier_info = get_rank_info(user.points or 0)


        leaderboard.append({

            "rank": index,

            "username": user.username,

            "avatar_url": user.avatar_url,

            "country": user.country,

            "points": user.points,

            "xp": user.xp,

            "level": user.level,

            "wins": user.wins,

            "losses": user.losses,

            "draws": user.draws,

            "rank_name": rank_tier_info["label"],

            "rank_tier": rank_tier_info["key"],

            "rank_icon_type": rank_tier_info["icon_type"],

            "rank_icon": rank_tier_info["icon"],

            "rank_color": rank_tier_info["color"]

        })



    return {


        "total_players": len(leaderboard),

        "leaderboard": leaderboard

    }