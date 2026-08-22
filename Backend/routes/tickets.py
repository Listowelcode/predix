from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session, joinedload

from database import get_db

from models import (
    Profile,
    Match,
    Prediction,
    PredictionTicket,
    TicketHistory
)

from dependencies import get_current_user

from services.ticket_refresh import sync_daily_tickets
from services.xp import check_and_award_matchday_bonus
from services.markets import is_market_allowed, market_points

from pydantic import BaseModel

from typing import List

import uuid



router = APIRouter(
    prefix="/tickets",
    tags=["Prediction Tickets"]
)





# =====================================
# SCHEMAS
# =====================================


class TicketPrediction(BaseModel):

    match_id: uuid.UUID

    prediction: str





class TicketCreate(BaseModel):

    predictions: List[TicketPrediction]









# =====================================
# CREATE TICKET
# =====================================


@router.post("/create")
def create_ticket(

    ticket: TicketCreate,

    db: Session = Depends(get_db),

    user: Profile = Depends(get_current_user)

):


    total_matches = len(ticket.predictions)



    if total_matches < 2:

        raise HTTPException(
            status_code=400,
            detail="Minimum 2 matches required"
        )



    if total_matches > 8:

        raise HTTPException(
            status_code=400,
            detail="Maximum 8 matches allowed"
        )



    if user.tickets <= 0:

        raise HTTPException(
            status_code=400,
            detail="No tickets available"
        )


    requested_match_ids = [item.match_id for item in ticket.predictions]

    if len(set(requested_match_ids)) != len(requested_match_ids):
        raise HTTPException(
            status_code=400,
            detail="Each match can be selected only once per ticket."
        )

    duplicate_rows = db.query(
        Prediction,
        Match
    ).join(
        Match,
        Prediction.match_id == Match.id
    ).filter(
        Prediction.user_id == user.id,
        Prediction.match_id.in_(requested_match_ids)
    ).all()

    if duplicate_rows:
        used_matches = []
        seen_match_ids = set()

        for _, used_match in duplicate_rows:
            if used_match.id in seen_match_ids:
                continue
            seen_match_ids.add(used_match.id)
            used_matches.append(
                f"{used_match.home_team} vs {used_match.away_team}"
            )

        raise HTTPException(
            status_code=409,
            detail=(
                "You already have a ticket containing: "
                + ", ".join(used_matches)
                + ". Choose different matches."
            )
        )


    fixed_predictions = {"HOME_WIN", "AWAY_WIN", "DRAW"}


    possible_points = 0

    matchdays = set()



    for item in ticket.predictions:



        prediction_code = item.prediction.upper()
        if prediction_code not in fixed_predictions and not prediction_code.startswith(("OVER_", "UNDER_")):
            raise HTTPException(
                status_code=400,
                detail="Invalid prediction"
            )



        match = db.query(Match).filter(

            Match.id == item.match_id

        ).first()



        if not match:

            raise HTTPException(

                status_code=404,

                detail="Match not found"

            )



        if match.status != "UPCOMING":

            raise HTTPException(
                status_code=400,
                detail="Match is closed"
            )

        if not is_market_allowed(match, prediction_code):
            raise HTTPException(
                status_code=400,
                detail="This market is not available for the selected match"
            )



        matchdays.add(match.match_date.date())



        possible_points += market_points(match, prediction_code)





    ticket_number = (

        "PDX-"

        + str(uuid.uuid4())[:8].upper()

    )





    new_ticket = PredictionTicket(

        user_id=user.id,

        ticket_number=ticket_number,

        total_matches=total_matches,

        possible_points=possible_points,

        status="PENDING"

    )



    db.add(new_ticket)

    db.flush()





    for item in ticket.predictions:



        prediction = Prediction(

            user_id=user.id,

            match_id=item.match_id,

            ticket_id=new_ticket.id,

            prediction=item.prediction.upper()

        )


        db.add(prediction)



    db.flush()

    # Matchday-completion XP bonus — no-op for any date the user
    # hasn't now fully covered, or has already claimed.
    check_and_award_matchday_bonus(user, db, matchdays)



    user.tickets -= 1





    history = TicketHistory(

        user_id=user.id,

        amount=-1,

        action="USED"

    )


    db.add(history)



    db.commit()



    db.refresh(new_ticket)



    # If that last ticket just brought the user to 0, kick off the
    # daily refresh cycle immediately rather than waiting for their
    # next request.
    db.refresh(user)

    sync_daily_tickets(user, db)




    return {

        "message":"Ticket created successfully",

        "ticket_number":new_ticket.ticket_number,

        "status":new_ticket.status,

        "possible_points":new_ticket.possible_points

    }









# =====================================
# GET MY TICKETS
# =====================================

@router.get("/my")
def get_my_tickets(

    db: Session = Depends(get_db),

    user: Profile = Depends(get_current_user)

):


    # Eager-load every ticket's predictions AND each prediction's
    # match in the same query (a couple of JOINs total) instead of
    # firing a separate query per ticket and another per
    # prediction. This is what previously turned a page showing,
    # say, 10 tickets x 4 matches each into 40+ round-trips to the
    # database on every load.
    tickets = db.query(
        PredictionTicket
    ).options(

        joinedload(PredictionTicket.predictions)
        .joinedload(Prediction.match)

    ).filter(

        PredictionTicket.user_id == user.id

    ).order_by(

        PredictionTicket.created_at.desc()

    ).all()



    active = []

    past = []



    for ticket in tickets:

        predictions = ticket.predictions



        ticket_data = {

            "ticket_id": str(ticket.id),

            "ticket_number": ticket.ticket_number,

            "matches": ticket.total_matches,

            "possible_points": ticket.possible_points,

            "points_won": ticket.points_won or 0,

            "status": ticket.status,

            "created_at": ticket.created_at,

            "predictions": []

        }




        for prediction in predictions:


            match = prediction.match



            if match:


                ticket_data["predictions"].append({

                    "match_id": str(match.id),

                    "teams":
                    f"{match.home_team} vs {match.away_team}",

                    "home_team":
                    match.home_team,

                    "away_team":
                    match.away_team,

                    "home_logo":
                    match.home_logo,

                    "away_logo":
                    match.away_logo,

                    "prediction":
                    prediction.prediction,

                    "match_status":
                    match.status,

                    # Per-leg outcome — WON / LOST while still PENDING
                    # until that specific match is settled. This is
                    # independent of the ticket's overall status, so a
                    # ticket can stay "active" while individual legs
                    # already show as won/lost.
                    "result":
                    prediction.status or "PENDING",

                    "points_won":
                    prediction.points_won or 0

                })




        if ticket.status == "PENDING":

            active.append(ticket_data)


        else:

            past.append(ticket_data)




    return {


        "total_tickets": len(tickets),


        "active_tickets": active,


        "past_tickets": past


    }
# =====================================
# GET SINGLE TICKET
# =====================================


@router.get("/{ticket_number}")
def get_ticket_details(

    ticket_number:str,

    db:Session = Depends(get_db),

    user:Profile = Depends(get_current_user)

):


    ticket = db.query(

        PredictionTicket

    ).filter(

        PredictionTicket.ticket_number == ticket_number,

        PredictionTicket.user_id == user.id

    ).first()



    if not ticket:

        raise HTTPException(

            status_code=404,

            detail="Ticket not found"

        )





    matches=[]



    for prediction in ticket.predictions:



        match = prediction.match



        matches.append({

            "teams":

            f"{match.home_team} vs {match.away_team}",

            "home_team":

            match.home_team,

            "away_team":

            match.away_team,

            "home_logo":

            match.home_logo,

            "away_logo":

            match.away_logo,


            "prediction":

            prediction.prediction,


            "status":

            match.status,

            # Per-leg outcome (WON / LOST / PENDING), independent of
            # the match's own UPCOMING/LIVE/FINISHED status.
            "result":

            prediction.status or "PENDING",


            "points":

            prediction.points_won

        })





    return {


        "ticket_number":

        ticket.ticket_number,


        "status":

        ticket.status,


        "possible_points":

        ticket.possible_points,


        "points_won":

        ticket.points_won,


        "matches":

        matches


    }