from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from sqlalchemy import func

from database import get_db

from services.ranks import get_rank_info, get_rank_progress
from services.level import calculate_level
from services.badges import sync_badges
from services.ticket_refresh import sync_daily_tickets

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



    # Keep the daily ticket cycle current before reading tickets off
    # this profile below.
    sync_daily_tickets(player, db)





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
    # Catch this user up on any rank/milestone badge their current
    # points or wins already qualify them for, in case it was never
    # awarded live (e.g. seeded data, or stats that changed outside
    # the normal winning-prediction flow). Cheap no-op if they're
    # already fully up to date.

    sync_badges(db, player)
    db.commit()

    badges = []


    for user_badge in player.badges:


        badges.append({

            "name": user_badge.badge.name,

            "description": user_badge.badge.description,

            "icon": user_badge.badge.icon,

            "rarity": user_badge.badge.rarity or "Common",

            "earned_at": user_badge.earned_at

        })







    # =====================================
    # RANK TIER (points-based)
    # =====================================

    rank_tier_info = get_rank_info(
        player.points or 0
    )

    rank_progress = get_rank_progress(
        player.points or 0
    )



    # =====================================
    # RESPONSE
    # =====================================


    return {


        "username": player.username,


        "avatar_url": player.avatar_url,


        "country": player.country,


        "rank": rank,


        "points": player.points or 0,


        "xp": player.xp or 0,
        
        "tickets": player.tickets or 0,

        # When set, the frontend uses this to render a "renews in
        # Xh Ym" countdown on the tickets card. NULL means the user
        # hasn't depleted their initial free tickets yet, so no
        # daily cycle/timer is running.
        "next_ticket_reset": player.next_ticket_reset,


        "level": calculate_level(
            player.xp
        ),


        # Tier name, e.g. "Bronze", "Platinum", "Legend" — driven
        # entirely by total points, matching the rank table.
        "rank_name": rank_tier_info["label"],

        "rank_tier": rank_tier_info["key"],

        "rank_icon_type": rank_tier_info["icon_type"],

        "rank_icon": rank_tier_info["icon"],

        "rank_color": rank_tier_info["color"],

        "rank_progress": rank_progress,



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