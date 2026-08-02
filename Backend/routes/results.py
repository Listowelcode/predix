from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from services.level import calculate_level
from services.badges import award_badge

from database import get_db

from models import (
    Match,
    Prediction,
    PredictionTicket,
    Profile
)

from dependencies import require_admin

from pydantic import BaseModel



router = APIRouter(
    prefix="/results",
    tags=["Match Results"]
)





# ===============================
# RESULT SCHEMA
# ===============================

class ResultUpdate(BaseModel):

    home_score: int

    away_score: int





# ===============================
# ADMIN SET RESULT
# ===============================

@router.post("/{match_id}")
def settle_match(

    match_id: str,

    result: ResultUpdate,

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



    if match.status == "FINISHED":

        raise HTTPException(
            status_code=400,
            detail="Match already settled"
        )





    # NOTE: There is intentionally no "wait until the match has
    # ended" time-gate here. Settling is an admin-only action
    # (see require_admin above) — once an admin has the final
    # score, they can submit it immediately. A time-based gate
    # was previously enforced here, but it compared an admin-
    # entered match_date (effectively local time) against
    # datetime.utcnow(), which could keep a match locked for far
    # longer than intended depending on the admin's timezone.
    # The only real guard needed is that a match can't be
    # settled twice, which is already checked above.





    # =================================
    # UPDATE MATCH RESULT
    # =================================

    match.home_score = result.home_score

    match.away_score = result.away_score




    if result.home_score > result.away_score:

        winner = "HOME_WIN"


    elif result.away_score > result.home_score:

        winner = "AWAY_WIN"


    else:

        winner = "DRAW"



    match.winner = winner

    match.status = "FINISHED"





    # =================================
    # UPDATE PREDICTIONS
    # =================================

    predictions = db.query(
        Prediction
    ).filter(
        Prediction.match_id == match.id
    ).all()



    correct_predictions = 0



    for prediction in predictions:


        user = db.query(Profile).filter(
            Profile.id == prediction.user_id
        ).first()



        if prediction.prediction == winner:


            if winner == "HOME_WIN":

                points = match.home_win_points


            elif winner == "AWAY_WIN":

                points = match.away_win_points


            else:

                points = match.draw_points




            prediction.points_won = points


            correct_predictions += 1




            if user:


                user.points += points

                user.xp += points


                user.level = calculate_level(
                    user.xp
                )


                user.wins += 1



                # ===============================
                # BADGES
                # ===============================

                award_badge(
                    db,
                    user,
                    "First Win"
                )



                if user.points >= 1000:

                    award_badge(
                        db,
                        user,
                        "Legend"
                    )



                if user.level >= 2:

                    award_badge(
                        db,
                        user,
                        "Bronze Predictor"
                    )



                if user.level >= 3:

                    award_badge(
                        db,
                        user,
                        "Silver Predictor"
                    )



                if user.level >= 4:

                    award_badge(
                        db,
                        user,
                        "Gold Predictor"
                    )



                if user.level >= 5:

                    award_badge(
                        db,
                        user,
                        "Elite Predictor"
                    )




        else:

            prediction.points_won = 0







    # =================================
    # UPDATE TICKETS
    # =================================

    affected_tickets = db.query(

        PredictionTicket

    ).join(

        Prediction

    ).filter(

        Prediction.match_id == match.id

    ).distinct().all()





    for ticket in affected_tickets:



        ticket_predictions = db.query(
            Prediction
        ).filter(
            Prediction.ticket_id == ticket.id
        ).all()



        unfinished_matches = 0



        for prediction in ticket_predictions:


            prediction_match = db.query(
                Match
            ).filter(
                Match.id == prediction.match_id
            ).first()



            if prediction_match.status != "FINISHED":

                unfinished_matches += 1





        # Still waiting for other matches

        if unfinished_matches > 0:


            ticket.status = "PENDING"

            continue






        # Ticket completed

        total_points = sum(

            prediction.points_won

            for prediction in ticket_predictions

        )



        ticket.points_won = total_points





        ticket_user = db.query(Profile).filter(
            Profile.id == ticket.user_id
        ).first()





        if total_points > 0:


            ticket.status = "WON"



            # ===============================
            # WINNING STREAK
            # ===============================

            if ticket_user:


                ticket_user.current_streak += 1



                if ticket_user.current_streak > ticket_user.best_streak:

                    ticket_user.best_streak = ticket_user.current_streak




                if ticket_user.current_streak >= 5:

                    award_badge(
                        db,
                        ticket_user,
                        "Hot Streak"
                    )





        else:


            ticket.status = "LOST"



            if ticket_user:

                ticket_user.current_streak = 0



    db.commit()


    db.refresh(match)



    return {


        "message": "Match result settled successfully",


        "match": {


            "home": match.home_team,


            "away": match.away_team,


            "score": f"{match.home_score}-{match.away_score}",


            "winner": match.winner

        },


        "predictions_checked": len(predictions),


        "correct_predictions": correct_predictions

    }