from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Match,
    Prediction,
    Profile
)

from dependencies import require_admin

from pydantic import BaseModel

from datetime import datetime



router = APIRouter(
    prefix="/admin/matches",
    tags=["Admin Matches"]
)





# =====================================
# SCHEMAS
# =====================================


class MatchCreate(BaseModel):

    home_team: str

    away_team: str

    league: str

    match_date: datetime

    kickoff_time: str

    home_win_points: int

    away_win_points: int

    draw_points: int





class MatchUpdate(BaseModel):

    home_team: str | None = None

    away_team: str | None = None

    league: str | None = None

    match_date: datetime | None = None

    kickoff_time: str | None = None

    home_win_points: int | None = None

    away_win_points: int | None = None

    draw_points: int | None = None





# =====================================
# GET ALL MATCHES
# =====================================


@router.get("")
def get_matches(

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    matches = db.query(
        Match
    ).order_by(
        Match.match_date.desc()
    ).all()



    return matches





# =====================================
# CREATE MATCH
# =====================================


@router.post("")
def create_match(

    data: MatchCreate,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    match = Match(

        home_team=data.home_team,

        away_team=data.away_team,

        league=data.league,

        match_date=data.match_date,

        kickoff_time=data.kickoff_time,

        home_win_points=data.home_win_points,

        away_win_points=data.away_win_points,

        draw_points=data.draw_points,

        status="UPCOMING"

    )



    db.add(match)

    db.commit()

    db.refresh(match)



    return {

        "message": "Match created successfully",

        "match": match

    }





# =====================================
# UPDATE MATCH
# =====================================


@router.put("/{match_id}")
def update_match(

    match_id: str,

    data: MatchUpdate,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    match = db.query(
        Match
    ).filter(
        Match.id == match_id
    ).first()



    if not match:

        raise HTTPException(

            status_code=404,

            detail="Match not found"

        )



    updates = data.dict(
        exclude_unset=True
    )



    for key, value in updates.items():

        setattr(
            match,
            key,
            value
        )



    db.commit()

    db.refresh(match)



    return {

        "message": "Match updated successfully",

        "match": match

    }





# =====================================
# DELETE MATCH
# =====================================


@router.delete("/{match_id}")
def delete_match(

    match_id: str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    match = db.query(
        Match
    ).filter(
        Match.id == match_id
    ).first()



    if not match:

        raise HTTPException(

            status_code=404,

            detail="Match not found"

        )



    predictions = db.query(
        Prediction
    ).filter(
        Prediction.match_id == match.id
    ).count()



    if predictions > 0:

        raise HTTPException(

            status_code=400,

            detail="Cannot delete match with existing predictions"

        )



    db.delete(match)

    db.commit()



    return {

        "message": "Match deleted successfully",

        "match_id": match_id

    }





# =====================================
# VIEW MATCH PREDICTIONS
# =====================================


@router.get("/{match_id}/predictions")
def match_predictions(

    match_id: str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    match = db.query(
        Match
    ).filter(
        Match.id == match_id
    ).first()



    if not match:

        raise HTTPException(

            status_code=404,

            detail="Match not found"

        )




    predictions = db.query(
        Prediction
    ).filter(
        Prediction.match_id == match.id
    ).all()



    home = 0

    away = 0

    draw = 0



    for prediction in predictions:


        if prediction.prediction == "HOME_WIN":

            home += 1


        elif prediction.prediction == "AWAY_WIN":

            away += 1


        else:

            draw += 1





    return {


        "match": f"{match.home_team} vs {match.away_team}",


        "predictions": {

            "HOME_WIN": home,

            "DRAW": draw,

            "AWAY_WIN": away

        },


        "total_predictions": len(predictions)

    }