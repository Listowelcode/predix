from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Season,
    SeasonPlayer,
    Profile
)


router = APIRouter(
    prefix="/seasons",
    tags=["Season Leaderboard"]
)


# ==========================================
# GET SEASON LEADERBOARD
# ==========================================

@router.get("/{season_id}/leaderboard")
def get_season_leaderboard(

    season_id: str,

    db: Session = Depends(get_db)

):


    # ============================
    # CHECK SEASON
    # ============================

    season = db.query(
        Season
    ).filter(
        Season.id == season_id
    ).first()


    if not season:

        raise HTTPException(
            status_code=404,
            detail="Season not found"
        )



    # ============================
    # GET PLAYERS
    # ============================

    players = db.query(
        SeasonPlayer
    ).filter(

        SeasonPlayer.season_id == season.id

    ).order_by(

        SeasonPlayer.season_points.desc()

    ).all()



    leaderboard = []



    rank = 1


    for player in players:


        user = db.query(
            Profile
        ).filter(

            Profile.id == player.user_id

        ).first()



        if not user:
            continue



        leaderboard.append({

            "rank": rank,

            "username": user.username,

            "country": user.country,

            "season_points": player.season_points,

            "matches_played": player.matches_played,

            "wins": player.wins,

            "losses": player.losses,

            "draws": player.draws

        })


        rank += 1



    return {

        "season": season.name,

        "status": season.status,

        "leaderboard": leaderboard

    }