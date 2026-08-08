from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Season,
    SeasonEntry,
    PredictionTicket,
    Prediction,
    Match,
    Profile
)

from dependencies import get_current_user

import uuid





router = APIRouter(
    prefix="/seasons",
    tags=["Season Play"]
)





# =====================================
# JOIN SEASON
# =====================================


@router.post("/{season_id}/join")
def join_season(

    season_id: str,

    db: Session = Depends(get_db),

    user: Profile = Depends(get_current_user)

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



    if season.status != "ACTIVE":

        raise HTTPException(
            status_code=400,
            detail="Season is not active"
        )



    existing = db.query(
        SeasonEntry
    ).filter(

        SeasonEntry.season_id == season.id,

        SeasonEntry.user_id == user.id

    ).first()



    if existing:

        raise HTTPException(
            status_code=400,
            detail="Already joined this season"
        )



    entry = SeasonEntry(

        season_id=season.id,

        user_id=user.id,

        status="ACTIVE"

    )


    db.add(entry)

    db.commit()

    db.refresh(entry)



    return {

        "message":
        "Joined season successfully",

        "season":
        season.name

    }









# =====================================
# GET SEASON MATCHES
# =====================================


@router.get("/{season_id}/matches")
def get_season_matches(

    season_id:str,

    db:Session = Depends(get_db)

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



    matches = db.query(
        Match
    ).filter(

        Match.season_id == season.id

    ).all()



    return matches







# =====================================
# CREATE SEASON TICKET
# =====================================


@router.post("/{season_id}/ticket")
def create_season_ticket(

    season_id:str,

    match_ids:list[str],

    db:Session = Depends(get_db),

    user:Profile = Depends(get_current_user)

):


    entry = db.query(
        SeasonEntry
    ).filter(

        SeasonEntry.season_id == season_id,

        SeasonEntry.user_id == user.id

    ).first()



    if not entry:

        raise HTTPException(
            status_code=400,
            detail="Join season first"
        )



    if entry.status != "ACTIVE":

        raise HTTPException(
            status_code=400,
            detail="You are eliminated"
        )



    if len(match_ids) < 4:

        raise HTTPException(
            status_code=400,
            detail="Minimum 4 matches required"
        )



    ticket = PredictionTicket(

        user_id=user.id,

        ticket_number=str(uuid.uuid4())[:8],

        total_matches=len(match_ids),

        ticket_type="SEASON",

        season_id=season_id,

        status="PENDING"

    )



    db.add(ticket)

    db.commit()

    db.refresh(ticket)



    return {

        "message":
        "Season ticket created",

        "ticket_id":
        ticket.id

    }









# =====================================
# SEASON BOARD
# =====================================


@router.get("/{season_id}/board")
def season_board(

    season_id:str,

    db:Session = Depends(get_db)

):


    entries = db.query(
        SeasonEntry
    ).filter(

        SeasonEntry.season_id == season_id

    ).all()



    board=[]



    for entry in entries:


        user=db.query(
            Profile
        ).filter(

            Profile.id==entry.user_id

        ).first()



        board.append({

            "username":
            user.username,

            "status":
            entry.status

        })



    return board