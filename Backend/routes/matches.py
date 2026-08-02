from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Match,
    Profile,
    Prediction,
    PredictionTicket
)

from schemas import (
    MatchResponse,
    MatchUpdate
)

from dependencies import require_admin

from services.storage import upload_image

from typing import List

from datetime import datetime





router = APIRouter(
    prefix="/matches",
    tags=["Matches"]
)





# =====================================
# CREATE MATCH (ADMIN)
# =====================================


@router.post(
    "/create",
    response_model=MatchResponse
)
def create_match(


    home_team: str = Form(...),

    away_team: str = Form(...),


    league: str = Form(None),


    match_date: datetime = Form(...),


    kickoff_time: str = Form(None),



    home_win_points: int = Form(0),

    away_win_points: int = Form(0),

    draw_points: int = Form(0),



    home_logo: UploadFile = File(None),

    away_logo: UploadFile = File(None),



    db: Session = Depends(get_db),


    admin: Profile = Depends(require_admin)


):


    try:


        home_logo_url = None

        away_logo_url = None




        # ==========================
        # UPLOAD HOME LOGO
        # ==========================

        if home_logo:


            home_logo_url = upload_image(

                home_logo.file.read(),

                home_logo.filename,

                home_logo.content_type

            )





        # ==========================
        # UPLOAD AWAY LOGO
        # ==========================

        if away_logo:


            away_logo_url = upload_image(

                away_logo.file.read(),

                away_logo.filename,

                away_logo.content_type

            )





        match = Match(


            home_team=home_team,


            away_team=away_team,


            league=league,


            match_date=match_date,


            kickoff_time=kickoff_time,



            home_logo=home_logo_url,


            away_logo=away_logo_url,



            home_win_points=home_win_points,


            away_win_points=away_win_points,


            draw_points=draw_points,


            status="UPCOMING"


        )



        db.add(match)

        db.commit()

        db.refresh(match)



        return match




    except Exception as e:


        db.rollback()


        raise HTTPException(

            status_code=500,

            detail=f"Match creation failed: {str(e)}"

        )









# =====================================
# GET ALL MATCHES
# =====================================


@router.get(
    "",
    response_model=List[MatchResponse]
)
def get_matches(


    db: Session = Depends(get_db)

):


    return db.query(
        Match
    ).order_by(

        Match.match_date

    ).all()









@router.delete("/{match_id}")
def delete_match(

    match_id: str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    match = db.query(Match).filter(
        Match.id == match_id
    ).first()


    if not match:

        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )



    # ===============================
    # FIND PREDICTIONS USING MATCH
    # ===============================

    predictions = db.query(
        Prediction
    ).filter(

        Prediction.match_id == match.id

    ).all()



    affected_tickets = set()



    for prediction in predictions:


        if prediction.ticket_id:

            affected_tickets.add(
                prediction.ticket_id
            )



        db.delete(prediction)





    # ===============================
    # REMOVE EMPTY TICKETS
    # ===============================

    for ticket_id in affected_tickets:


        ticket = db.query(
            PredictionTicket
        ).filter(

            PredictionTicket.id == ticket_id

        ).first()



        if ticket:


            remaining_predictions = db.query(
                Prediction
            ).filter(

                Prediction.ticket_id == ticket.id

            ).count()



            if remaining_predictions == 0:


                db.delete(ticket)





    # ===============================
    # DELETE MATCH
    # ===============================

    db.delete(match)


    db.commit()



    return {


        "message":
        "Match deleted successfully"


    }
# =====================================
# UPDATE MATCH
# =====================================


@router.patch("/{match_id}")
def update_match(


    match_id: str,


    update: MatchUpdate,


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




    changes = update.model_dump(

        exclude_unset=True

    )



    for key,value in changes.items():


        setattr(

            match,

            key,

            value

        )




    db.commit()

    db.refresh(match)




    return {


        "message":
        "Match updated successfully",



        "match":{


            "id":
            str(match.id),


            "home_team":
            match.home_team,


            "away_team":
            match.away_team,


            "home_logo":
            match.home_logo,


            "away_logo":
            match.away_logo,


            "home_win_points":
            match.home_win_points,


            "away_win_points":
            match.away_win_points,


            "draw_points":
            match.draw_points


        }

    }









# =====================================
# TODAY'S MATCHES
# =====================================


@router.get(
    "/today",
    response_model=List[MatchResponse]
)
def todays_matches(


    db: Session = Depends(get_db)

):


    today = datetime.utcnow()



    start = today.replace(

        hour=0,

        minute=0,

        second=0,

        microsecond=0

    )



    end = today.replace(

        hour=23,

        minute=59,

        second=59,

        microsecond=999999

    )




    return db.query(
        Match
    ).filter(

        Match.match_date >= start,


        Match.match_date <= end

    ).all()