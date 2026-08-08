from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Prediction,
    Match,
    Profile,
    TicketHistory
)

from schemas import (
    PredictionCreate,
    PredictionResponse
)

from dependencies import get_current_user

from services.badges import award_badge

from typing import List

from datetime import datetime



router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)





# =====================================
# CREATE PREDICTION
# =====================================

@router.post(
    "/create",
    response_model=PredictionResponse
)
def create_prediction(

    prediction: PredictionCreate,

    db: Session = Depends(get_db),

    user: Profile = Depends(get_current_user)

):


    # Check match exists

    match = db.query(Match).filter(
        Match.id == prediction.match_id
    ).first()



    if not match:

        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )



    # Check match status

    if match.status != "UPCOMING":

        raise HTTPException(
            status_code=400,
            detail="Voting closed for this match"
        )



    # ✅ ADD VALIDATION HERE

    if prediction.prediction not in [

        "HOME_WIN",

        "AWAY_WIN",

        "DRAW"

    ]:

        raise HTTPException(

            status_code=400,

            detail="Invalid prediction type"

        )



    # Check if user already predicted

    existing_prediction = db.query(
        Prediction
    ).filter(

        Prediction.user_id == user.id,

        Prediction.match_id == match.id

    ).first()



    if existing_prediction:

        raise HTTPException(

            status_code=400,

            detail="You already predicted this match"

        )



    # Check tickets

    if user.tickets <= 0:

        raise HTTPException(

            status_code=400,

            detail="No tickets available"

        )



    # Create prediction

    new_prediction = Prediction(

        user_id=user.id,

        match_id=match.id,

        prediction=prediction.prediction

    )


    user.tickets -= 1


    db.add(new_prediction)

    db.commit()

    db.refresh(new_prediction)



    # ===============================
    # BADGES
    # ===============================
    # Awarded the moment a user makes their very first prediction —
    # doesn't matter if it ends up right or wrong.

    award_badge(
        db,
        user,
        "First Prediction"
    )

    db.commit()


    return new_prediction

# =====================================
# MY PREDICTIONS
# =====================================

@router.get(
    "/my",
    response_model=List[PredictionResponse]
)
def my_predictions(

    db: Session = Depends(get_db),

    user: Profile = Depends(get_current_user)

):


    predictions = db.query(
        Prediction
    ).filter(

        Prediction.user_id == user.id

    ).all()



    return predictions