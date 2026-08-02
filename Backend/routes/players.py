from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from sqlalchemy import func

from database import get_db

from services.ranks import get_rank
from services.level import calculate_level

from models import (
    Profile,
    PredictionTicket,
    Prediction,
    UserBadge,
    Badge
)





router = APIRouter(
    prefix="/players",
    tags=["Players"]
)





# =====================================
# GET PLAYER PROFILE
# =====================================


@router.get("/{username}")
def get_player_profile(

    username: str,

    db: Session = Depends(get_db)

):


    # Find user ignoring case

    player = db.query(Profile).filter(

        func.lower(Profile.username) == username.lower()

    ).first()



    if not player:

        raise HTTPException(

            status_code=404,

            detail="Player not found"

        )





    # =====================================
    # CALCULATE RANK
    # =====================================

    players_above = db.query(Profile).filter(

        Profile.points > player.points

    ).count()



    rank = players_above + 1





    # =====================================
    # TICKET STATS
    # =====================================

    tickets = db.query(
        PredictionTicket
    ).filter(

        PredictionTicket.user_id == player.id

    ).all()



    tickets_played = len(tickets)



    tickets_won = len([

        ticket for ticket in tickets

        if ticket.status == "WON"

    ])



    tickets_lost = len([

        ticket for ticket in tickets

        if ticket.status == "LOST"

    ])





    # =====================================
    # PREDICTION ACCURACY
    # =====================================

    predictions = db.query(

        Prediction

    ).filter(

        Prediction.user_id == player.id

    ).all()



    correct_predictions = len([

        prediction for prediction in predictions

        if prediction.points_won > 0

    ])



    total_predictions = len(predictions)



    if total_predictions > 0:

        accuracy = round(

            (correct_predictions / total_predictions) * 100,

            2

        )

    else:

        accuracy = 0





    # =====================================
    # BADGES
    # =====================================

    badges = []


    for user_badge in player.badges:


        badges.append({

            "name": user_badge.badge.name,

            "description": user_badge.badge.description,

            "icon": user_badge.badge.icon,

            "earned_at": user_badge.earned_at

        })







    # =====================================
    # RESPONSE
    # =====================================


    return {


        "username": player.username,


        "avatar_url": player.avatar_url,


        "rank": rank,


        "points": player.points or 0,


        "xp": player.xp or 0,
        
        "tickets": player.tickets or 0,


        "level": calculate_level(
            player.xp
        ),


        "rank_name": get_rank(
            player.level
        ),



        "badges": badges,



        "stats": {


            "wins": player.wins,


            "losses": player.losses,


            "draws": player.draws,


            "tickets_played": tickets_played,


            "tickets_won": tickets_won,


            "tickets_lost": tickets_lost,


            "current_streak": player.current_streak,


            "best_streak": player.best_streak,


            "accuracy": f"{accuracy}%"

        }

    }