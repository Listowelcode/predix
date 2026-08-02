from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db

from models import (
    Profile,
    PredictionTicket,
    Prediction
)

from dependencies import require_admin

from pydantic import BaseModel





router = APIRouter(
    prefix="/admin/users",
    tags=["Admin Users"]
)





# =====================================
# SCHEMAS
# =====================================


class PointsUpdate(BaseModel):

    amount: int

    reason: str





# =====================================
# GET ALL USERS
# =====================================


@router.get("")
def get_users(

    search: str | None = Query(None),

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    query = db.query(Profile)



    if search:


        query = query.filter(

            func.lower(Profile.username)
            .contains(
                search.lower()
            )

        )



    users = query.order_by(

        func.coalesce(
            Profile.points,
            0
        ).desc()

    ).all()





    user_list = []



    for index, user in enumerate(
        users,
        start=1
    ):


        user_list.append({


            "rank": index,


            "id": str(user.id),


            "username": user.username,


            "email": user.email,


            "avatar_url": user.avatar_url,


            "role": user.role or "USER",


            "points": user.points or 0,


            "xp": user.xp or 0,


            "tickets": user.tickets or 0,


            "level": user.level or 1,


            "wins": user.wins or 0,


            "losses": user.losses or 0,


            "draws": user.draws or 0,


            "current_streak": user.current_streak or 0,


            "best_streak": user.best_streak or 0,


            "created_at": user.created_at

        })



    return user_list







# =====================================
# GET USER DETAILS
# =====================================


@router.get("/{user_id}")
def get_user_details(

    user_id: str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    user = db.query(Profile).filter(

        Profile.id == user_id

    ).first()



    if not user:


        raise HTTPException(

            status_code=404,

            detail="User not found"

        )





    tickets = db.query(

        PredictionTicket

    ).filter(

        PredictionTicket.user_id == user.id

    ).all()





    predictions = db.query(

        Prediction

    ).filter(

        Prediction.user_id == user.id

    ).all()





    return {


        "rank": None,


        "username": user.username,


        "email": user.email,


        "avatar_url": user.avatar_url,



        "stats": {


            "points": user.points or 0,


            "xp": user.xp or 0,


            "level": user.level or 1,


            "wins": user.wins or 0,


            "losses": user.losses or 0,


            "draws": user.draws or 0,


            "current_streak": user.current_streak or 0,


            "best_streak": user.best_streak or 0


        },



        "tickets": {


            "played": len(tickets),


            "won": len([

                t for t in tickets

                if t.status == "WON"

            ]),


            "lost": len([

                t for t in tickets

                if t.status == "LOST"

            ])

        },



        "predictions": {


            "total": len(predictions),


            "correct": len([

                p for p in predictions

                if p.points_won > 0

            ])

        }

    }






@router.put("/{user_id}/points")
def update_points(

    user_id: str,

    data: PointsUpdate,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    user = db.query(Profile).filter(

        Profile.id == user_id

    ).first()



    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found"

        )



    current_points = user.points or 0

    current_xp = user.xp or 0



    # Update points

    user.points = current_points + data.amount


    if user.points < 0:

        user.points = 0



    # Update XP separately

    xp_reward = int(data.amount * 0.25)


    user.xp = current_xp + xp_reward



    db.commit()

    db.refresh(user)



    return {

        "message": "Points updated successfully",

        "username": user.username,

        "new_points": user.points,

        "new_xp": user.xp,

        "reason": data.reason

    }

# =====================================
# DELETE USER
# =====================================


@router.delete("/{user_id}")
def delete_user(

    user_id: str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    user = db.query(Profile).filter(

        Profile.id == user_id

    ).first()



    if not user:


        raise HTTPException(

            status_code=404,

            detail="User not found"

        )





    if (
        user.role or ""
    ).upper() == "ADMIN":


        raise HTTPException(

            status_code=400,

            detail="Cannot delete admin account"

        )





    db.query(
        Prediction
    ).filter(

        Prediction.user_id == user.id

    ).delete(
        synchronize_session=False
    )





    db.query(
        PredictionTicket
    ).filter(

        PredictionTicket.user_id == user.id

    ).delete(
        synchronize_session=False
    )





    username = user.username



    db.delete(user)

    db.commit()





    return {


        "message":
        "User deleted successfully",


        "deleted_user":
        username

    }