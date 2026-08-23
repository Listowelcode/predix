from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session, joinedload

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


    # Eager-load predictions + their matches in the ticket query
    # itself, and batch-fetch all the involved users in a single
    # extra query — replacing what used to be 1 (Profile) + 1
    # (Prediction) + N (Match) queries per ticket with 2 queries
    # total for the whole page.
    tickets = db.query(
        PredictionTicket
    ).options(

        joinedload(PredictionTicket.predictions)
        .joinedload(Prediction.match)

    ).order_by(

        PredictionTicket.created_at.desc()

    ).all()



    user_ids = {ticket.user_id for ticket in tickets}

    users_by_id = {
        u.id: u
        for u in db.query(Profile).filter(Profile.id.in_(user_ids)).all()
    } if user_ids else {}



    result = []



    for ticket in tickets:


        user = users_by_id.get(ticket.user_id)



        predictions = ticket.predictions



        matches = []



        for prediction in predictions:


            match = prediction.match



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





        # Keep the ticket and its predictions for audit/history purposes. Admin
    # deletion is a soft delete and never refunds the user's ticket credit.
    ticket.status = "DELETED"
    db.commit()

    return {
        "message": "Ticket marked as deleted successfully. No ticket was refunded.",
        "ticket_id": str(ticket.id),
        "ticket_number": ticket.ticket_number,
        "status": ticket.status,
    }
