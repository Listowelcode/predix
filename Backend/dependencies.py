from fastapi import Depends, HTTPException

from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError

from sqlalchemy.orm import Session

from database import get_db

from models import Profile

from services.ticket_refresh import sync_daily_tickets

from dotenv import load_dotenv

import os



load_dotenv()



SECRET_KEY = os.getenv("SECRET_KEY")


ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)





# =====================================
# OAUTH2 JWT AUTH
# =====================================

oauth2_scheme = OAuth2PasswordBearer(

    tokenUrl="/auth/login"

)







def get_current_user(

    token: str = Depends(oauth2_scheme),

    db: Session = Depends(get_db)

):


    try:

        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]

        )


        user_id = payload.get(
            "user_id"
        )



        if not user_id:

            raise HTTPException(

                status_code=401,

                detail="Invalid token"

            )



    except JWTError:


        raise HTTPException(

            status_code=401,

            detail="Invalid token"

        )





    user = db.query(Profile).filter(

        Profile.id == user_id

    ).first()



    if not user:


        raise HTTPException(

            status_code=404,

            detail="User not found"

        )



    # Lazily apply/advance the daily ticket-refresh cycle before
    # this user is used anywhere downstream, so every authenticated
    # request always sees an up-to-date ticket balance.
    sync_daily_tickets(user, db)



    return user







# =====================================
# ADMIN ONLY ACCESS
# =====================================

def require_admin(

    current_user: Profile = Depends(get_current_user)

):


    if current_user.role != "ADMIN":


        raise HTTPException(

            status_code=403,

            detail="Admin access required"

        )


    return current_user