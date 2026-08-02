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
    Profile
)

from dependencies import require_admin



router = APIRouter(
    prefix="/admin/seasons",
    tags=["Season Rewards"]
)





# =====================================
# SETTLE SEASON & DISTRIBUTE REWARDS
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


    current_time = datetime.utcnow()



    if current_time < season.end_date:

        raise HTTPException(

            status_code=400,

            detail="Season has not ended yet"

        )





    # =====================================
    # GET USERS
    # =====================================


    users = db.query(
        Profile
    ).all()



    rewards_given = []





    # =====================================
    # SORT REWARD RULES
    # =====================================


    rules = sorted(

        season.reward_rules,

        key=lambda x: x["points"],

        reverse=True

    )





    # =====================================
    # CHECK USERS
    # =====================================


    for user in users:



        tickets = 0





        for reward in rules:



            if user.points >= reward["points"]:

                tickets = reward["tickets"]

                break





        # User did not qualify

        if tickets == 0:

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

            continue





        # =====================================
        # GIVE TICKETS
        # =====================================


        user.tickets += tickets





        reward_record = SeasonReward(

            season_id=season.id,

            user_id=user.id,

            points_at_end=user.points,

            tickets_awarded=tickets,

            claimed=True

        )



        db.add(reward_record)





        rewards_given.append({

            "username": user.username,

            "points": user.points,

            "tickets_added": tickets

        })







    # =====================================
    # END SEASON
    # =====================================


    season.status = "ENDED"





    db.commit()





    return {


        "message": "Season rewards distributed successfully",


        "season": season.name,


        "status": season.status,


        "rewards_distributed": len(rewards_given),


        "users": rewards_given

    }