from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from database import get_db

from models import Profile

from typing import List



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


        leaderboard.append({

            "rank": index,

            "username": user.username,

            "avatar_url": user.avatar_url,

            "points": user.points,

            "xp": user.xp,

            "level": user.level,

            "wins": user.wins,

            "losses": user.losses,

            "draws": user.draws

        })



    return {


        "total_players": len(leaderboard),

        "leaderboard": leaderboard

    }