from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from datetime import datetime

from database import get_db

from models import (
    Season,
    SeasonReward,
    SeasonPlayer,
    Profile
)

from dependencies import require_admin



router = APIRouter(
    prefix="/admin/seasons",
    tags=["Season Rewards"]
)





# =====================================
# SETTLE SEASON & DISTRIBUTE LEAGUE CARDS
# =====================================


@router.post("/{season_id}/settle")
def settle_season(

    season_id: str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    # =====================================
    # FIND SEASON
    # =====================================

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





    # =====================================
    # CHECK STATUS
    # =====================================

    if season.status == "ENDED":

        raise HTTPException(
            status_code=400,
            detail="Season already settled"
        )



    if season.status != "ACTIVE":

        raise HTTPException(
            status_code=400,
            detail="Only active seasons can be settled"
        )





    # =====================================
    # CHECK END DATE
    # =====================================

    if datetime.utcnow() < season.end_date:

        raise HTTPException(
            status_code=400,
            detail="Season has not ended yet"
        )





    # =====================================
    # CHECK REWARD RULES
    # =====================================

    if not season.reward_rules:

        raise HTTPException(
            status_code=400,
            detail="No reward rules configured"
        )


    if not isinstance(
        season.reward_rules,
        dict
    ):

        raise HTTPException(
            status_code=400,
            detail="Reward rules must be a dictionary"
        )





    # =====================================
    # GET SEASON PLAYERS RANKED
    # =====================================

    players = db.query(
        SeasonPlayer
    ).filter(
        SeasonPlayer.season_id == season.id
    ).order_by(
        SeasonPlayer.season_points.desc()
    ).all()



    if not players:

        raise HTTPException(
            status_code=400,
            detail="No players participated in this season"
        )





    rewards_given = []


    rank = 1





    # =====================================
    # DISTRIBUTE REWARDS
    # =====================================

    for player in players:


        user = db.query(
            Profile
        ).filter(
            Profile.id == player.user_id
        ).first()



        if not user:

            continue





        # Example reward_rules:

        # {
        #   "1":100,
        #   "2":50,
        #   "3":25,
        #   "4":10
        # }


        league_cards = season.reward_rules.get(
            str(rank),
            0
        )





        if league_cards <= 0:

            rank += 1

            continue





        # =====================================
        # PREVENT DUPLICATES
        # =====================================

        existing_reward = db.query(
            SeasonReward
        ).filter(

            SeasonReward.season_id == season.id,

            SeasonReward.user_id == user.id

        ).first()



        if existing_reward:

            rank += 1

            continue





        # =====================================
        # ADD LEAGUE CARDS TO USER
        # =====================================

        user.tickets += league_cards





        # =====================================
        # SAVE REWARD RECORD
        # =====================================

        reward = SeasonReward(

            season_id=season.id,

            user_id=user.id,

            points_at_end=player.season_points,

            survival_rank=rank,

            league_cards_awarded=league_cards,

            claimed=True

        )


        db.add(reward)





        rewards_given.append({

            "rank": rank,

            "username": user.username,

            "points": player.season_points,

            "league_cards": league_cards

        })



        rank += 1





    # =====================================
    # END SEASON
    # =====================================

    season.status = "ENDED"



    db.commit()



    return {


        "message":
        "Season settled successfully",


        "season":
        season.name,


        "status":
        season.status,


        "rewards_distributed":
        len(rewards_given),


        "rewards":
        rewards_given

    }
    
@router.post("/{season_id}/force-settle")
def force_settle_season(

    season_id: str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):

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


    season.end_date = datetime.utcnow()


    db.commit()


    return {
        "message": "Season forced to end. You can now settle rewards."
    }