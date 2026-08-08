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

from models import Profile

from dependencies import get_current_user

from services.storage import upload_image



router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)





# =====================================
# GET MY PROFILE
# =====================================

@router.get("/me")
def my_profile(

    user: Profile = Depends(get_current_user)

):


    return {


        "id":
        str(user.id),


        "username":
        user.username,


        "email":
        user.email,


        "avatar_url":
        user.avatar_url,


        "phone":
        user.phone,


        "country":
        user.country,


        "points":
        user.points,


        "tickets":
        user.tickets,


        "next_ticket_reset":
        user.next_ticket_reset,


        "wins":
        user.wins,


        "losses":
        user.losses,


        "draws":
        user.draws,


        "level":
        user.level,


        "xp":
        user.xp,


        "current_streak":
        user.current_streak,


        "best_streak":
        user.best_streak


    }






# =====================================
# UPDATE PROFILE
# =====================================


@router.put("/update")
def update_profile(


    username: str = Form(None),


    avatar: UploadFile = File(None),


    country: str = Form(None),


    db: Session = Depends(get_db),


    user: Profile = Depends(get_current_user)

):



    # ===============================
    # UPDATE USERNAME
    # ===============================


    if username:


        username = username.strip()



        if len(username) < 3:

            raise HTTPException(

                status_code=400,

                detail="Username must be at least 3 characters"

            )



        existing = db.query(Profile).filter(

            Profile.username == username

        ).first()



        if existing and existing.id != user.id:


            raise HTTPException(

                status_code=400,

                detail="Username already taken"

            )



        user.username = username







    # ===============================
    # UPDATE AVATAR
    # ===============================


    if avatar:


        allowed_types = [

            "image/jpeg",

            "image/png",

            "image/webp"

        ]



        if avatar.content_type not in allowed_types:


            raise HTTPException(

                status_code=400,

                detail="Only JPG, PNG and WEBP images allowed"

            )





        image_data = avatar.file.read()





        image_url = upload_image(

            image_data,

            avatar.filename,

            avatar.content_type

        )



        user.avatar_url = image_url



    # ===============================
    # UPDATE COUNTRY
    # ===============================

    if country:

        country = country.strip().upper()

        if len(country) != 2 or not country.isalpha():

            raise HTTPException(

                status_code=400,

                detail="Country must be a 2-letter code, e.g. GH"

            )

        user.country = country





    db.commit()


    db.refresh(user)





    return {


        "message":

        "Profile updated successfully",



        "username":

        user.username,



        "avatar_url":

        user.avatar_url,


        "country":

        user.country


    }