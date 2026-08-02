from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Profile,
    Match,
    Prediction,
    PredictionTicket,
    TicketHistory
)

from dependencies import get_current_user

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




    allowed_predictions = [

        "HOME_WIN",
        "AWAY_WIN",
        "DRAW"

    ]



    possible_points = 0



    for item in ticket.predictions:



        if item.prediction not in allowed_predictions:

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




        if item.prediction == "HOME_WIN":

            possible_points += match.home_win_points


        elif item.prediction == "AWAY_WIN":

            possible_points += match.away_win_points


        else:

            possible_points += match.draw_points





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

            prediction=item.prediction

        )


        db.add(prediction)





    user.tickets -= 1





    history = TicketHistory(

        user_id=user.id,

        amount=-1,

        action="USED"

    )


    db.add(history)



    db.commit()



    db.refresh(new_ticket)




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


    tickets = db.query(
        PredictionTicket
    ).filter(

        PredictionTicket.user_id == user.id

    ).order_by(

        PredictionTicket.created_at.desc()

    ).all()



    active = []

    past = []



    for ticket in tickets:


        predictions = db.query(
            Prediction
        ).filter(

            Prediction.ticket_id == ticket.id

        ).all()



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


            match = db.query(
                Match
            ).filter(

                Match.id == prediction.match_id

            ).first()



            if match:


                ticket_data["predictions"].append({

                    "match_id": str(match.id),

                    "teams":
                    f"{match.home_team} vs {match.away_team}",

                    "prediction":
                    prediction.prediction,

                    "match_status":
                    match.status

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


            "prediction":

            prediction.prediction,


            "status":

            match.status,


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