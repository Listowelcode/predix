from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from database import get_db
from sqlalchemy import func
from models import Profile

from schemas import (
    RegisterRequest,
    LoginRequest
)
from fastapi.security import OAuth2PasswordRequestForm
from security import (
    hash_password,
    verify_password,
    create_access_token
)



router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)





# =================================
# REGISTER
# =================================

@router.post("/register")
def register(

    user: RegisterRequest,

    db: Session = Depends(get_db)

):


    # Check existing email

    existing_email = db.query(Profile).filter(

        func.lower(Profile.email) == user.email.lower()

    ).first()



    if existing_email:

        raise HTTPException(

            status_code=400,

            detail="Email already registered"

        )



    # Check existing username

    existing_username = db.query(Profile).filter(

        func.lower(Profile.username) == user.username.lower()

    ).first()



    if existing_username:

        raise HTTPException(

            status_code=400,

            detail="Username already taken"

        )




    # Create user

    new_user = Profile(

        username=user.username,

        email=user.email,

        password_hash=hash_password(

            user.password

        )

    )



    db.add(new_user)

    db.commit()

    db.refresh(new_user)




    # Create JWT

    token = create_access_token(

        {

            "user_id": str(new_user.id)

        }

    )



    return {


        "message": "Account created successfully",


        "access_token": token,


        "token_type": "bearer",


        "user": {


            "id": str(new_user.id),


            "username": new_user.username,


            "email": new_user.email,


            "role": new_user.role


        }

    }









# =================================
# LOGIN
# =================================

# =================================
# LOGIN
# =================================
# =================================
# LOGIN
# =================================

@router.post("/login")
def login(

    form_data: OAuth2PasswordRequestForm = Depends(),

    db: Session = Depends(get_db)

):


    login_value = form_data.username



    # Search username OR email

    existing_user = db.query(Profile).filter(

        (func.lower(Profile.username) == login_value.lower()) |

        (func.lower(Profile.email) == login_value.lower())

    ).first()





    if not existing_user:


        raise HTTPException(

            status_code=404,

            detail="User not found"

        )





    # Verify password

    if not verify_password(

        form_data.password,

        existing_user.password_hash

    ):


        raise HTTPException(

            status_code=401,

            detail="Incorrect password"

        )






    token = create_access_token(

        {

            "user_id": str(existing_user.id)

        }

    )





    return {


        "access_token": token,


        "token_type": "bearer",


        "user": {


            "id": str(existing_user.id),


            "username": existing_user.username,


            "email": existing_user.email,


            "role": existing_user.role


        }


    }