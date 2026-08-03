from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Profile,
    PredictionTicket,
    Prediction,
    Match,
    TicketHistory
)

from dependencies import require_admin



router = APIRouter(
    prefix="/admin/tickets",
    tags=["Admin Tickets"]
)





# =====================================
# GET ALL TICKETS
# =====================================

@router.get("")
def get_all_tickets(

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    tickets = db.query(
        PredictionTicket
    ).order_by(

        PredictionTicket.created_at.desc()

    ).all()



    result = []



    for ticket in tickets:


        user = db.query(Profile).filter(

            Profile.id == ticket.user_id

        ).first()



        predictions = db.query(
            Prediction
        ).filter(

            Prediction.ticket_id == ticket.id

        ).all()



        matches = []



        for prediction in predictions:


            match = db.query(Match).filter(

                Match.id == prediction.match_id

            ).first()



            if match:


                matches.append({

                    "match_id": str(match.id),

                    "teams":
                    f"{match.home_team} vs {match.away_team}",

                    "home_team":
                    match.home_team,

                    "away_team":
                    match.away_team,

                    "prediction":
                    prediction.prediction,

                    "status":
                    match.status,

                    # Per-leg outcome — lets the admin see which
                    # individual matches in a still-active ticket have
                    # already been won/lost, vs. which are pending.
                    "result":
                    prediction.status or "PENDING"

                })





        result.append({


            "ticket_id":
            str(ticket.id),


            "ticket_number":
            ticket.ticket_number,


            "username":
            user.username if user else "Unknown",


            "user_id":
            str(ticket.user_id),


            "status":
            ticket.status,


            "matches":
            ticket.total_matches,


            "possible_points":
            ticket.possible_points,


            "points_won":
            ticket.points_won or 0,


            "created_at":
            ticket.created_at,


            "predictions":
            matches


        })





    return {


        "total":
        len(result),


        "tickets":
        result


    }









# =====================================
# DELETE TICKET
# =====================================

@router.delete("/{ticket_id}")
def delete_ticket(

    ticket_id: str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    ticket = db.query(
        PredictionTicket
    ).filter(

        PredictionTicket.id == ticket_id

    ).first()



    if not ticket:

        raise HTTPException(

            status_code=404,

            detail="Ticket not found"

        )





    user = db.query(Profile).filter(

        Profile.id == ticket.user_id

    ).first()





    # remove predictions first

    db.query(Prediction).filter(

        Prediction.ticket_id == ticket.id

    ).delete(

        synchronize_session=False

    )






    # refund ticket back to user

    if user:


        user.tickets += 1



        history = TicketHistory(

            user_id=user.id,

            amount=1,

            action="REFUNDED"

        )


        db.add(history)







    # delete ticket


    db.delete(ticket)



    db.commit()





    return {


        "message":

        "Ticket deleted successfully"


    }