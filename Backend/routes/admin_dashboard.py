from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db

from models import (
    Profile,
    Match,
    PredictionTicket
)

from dependencies import require_admin



router = APIRouter(
    prefix="/admin/dashboard",
    tags=["Admin Dashboard"]
)





# =====================================
# ADMIN DASHBOARD STATS
# =====================================


@router.get("/stats")
def admin_dashboard_stats(

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    # ================================
    # USERS
    # ================================


    total_users = db.query(
        Profile
    ).count()





    # ================================
    # MATCHES
    # ================================


    total_matches = db.query(
        Match
    ).count()



    upcoming_matches = db.query(
        Match
    ).filter(
        Match.status == "UPCOMING"
    ).count()



    finished_matches = db.query(
        Match
    ).filter(
        Match.status == "FINISHED"
    ).count()





    # ================================
    # TICKETS
    # ================================


    total_tickets = db.query(
        PredictionTicket
    ).count()



    pending_tickets = db.query(
        PredictionTicket
    ).filter(
        PredictionTicket.status == "PENDING"
    ).count()



    won_tickets = db.query(
        PredictionTicket
    ).filter(
        PredictionTicket.status == "WON"
    ).count()



    lost_tickets = db.query(
        PredictionTicket
    ).filter(
        PredictionTicket.status == "LOST"
    ).count()






    # ================================
    # POINTS
    # ================================


    total_points = db.query(

        func.sum(
            PredictionTicket.points_won
        )

    ).scalar() or 0






    return {


        "users": {

            "total": total_users

        },


        "matches": {

            "total": total_matches,

            "upcoming": upcoming_matches,

            "finished": finished_matches

        },


        "tickets": {

            "total": total_tickets,

            "pending": pending_tickets,

            "won": won_tickets,

            "lost": lost_tickets

        },


        "points": {

            "distributed": total_points

        }


    }