```python
import re
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Profile

from schemas import (
    RegisterRequest,
    LoginRequest
)

from security import (
    hash_password,
    verify_password,
    create_access_token
)

from services.xp import award_daily_login_xp


logger = logging.getLogger("predix.auth")


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

    # ---------------------------------
    # Check existing email
    # ---------------------------------

    existing_email = db.query(Profile).filter(
        func.lower(Profile.email) == user.email.lower()
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )


    # ---------------------------------
    # Check existing username
    # ---------------------------------

    existing_username = db.query(Profile).filter(
        func.lower(Profile.username) == user.username.lower()
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )


    # ---------------------------------
    # Validate phone number
    # ---------------------------------
    # Expects international format:
    # +233241234567

    if not re.match(r"^\+[1-9]\d{6,14}$", user.phone):

        raise HTTPException(
            status_code=400,
            detail="Enter a valid international phone number"
        )


    country_code = user.country.upper()


    # ---------------------------------
    # Check existing phone number
    # ---------------------------------

    existing_phone = db.query(Profile).filter(
        Profile.phone == user.phone
    ).first()

    if existing_phone:

        raise HTTPException(
            status_code=400,
            detail="Phone number already registered"
        )


    # ---------------------------------
    # Create user
    # ---------------------------------

    new_user = Profile(
        username=user.username,
        email=user.email,
        phone=user.phone,
        country=country_code,
        password_hash=hash_password(
            user.password
        )
    )


    db.add(new_user)

    try:

        db.commit()

        db.refresh(new_user)

    except Exception as exc:

        db.rollback()

        logger.exception(
            "Registration database error"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create account"
        )


    # ---------------------------------
    # Create JWT
    # ---------------------------------

    try:

        token = create_access_token(
            {
                "user_id": str(new_user.id)
            }
        )

    except Exception:

        logger.exception(
            "JWT creation failed during registration"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create authentication token"
        )


    return {

        "message": "Account created successfully",

        "access_token": token,

        "token_type": "bearer",

        "user": {

            "id": str(new_user.id),

            "username": new_user.username,

            "email": new_user.email,

            "country": new_user.country,

            "role": new_user.role

        }

    }


# =================================
# LOGIN
# =================================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # ---------------------------------
    # Get login value
    # ---------------------------------

    login_value = form_data.username.strip()

    if not login_value:

        raise HTTPException(
            status_code=400,
            detail="Username or email is required"
        )


    # ---------------------------------
    # Find user
    # ---------------------------------

    try:

        existing_user = db.query(Profile).filter(

            (
                func.lower(Profile.username)
                == login_value.lower()
            )

            |

            (
                func.lower(Profile.email)
                == login_value.lower()
            )

        ).first()

    except Exception:

        logger.exception(
            "Database error while looking up login user"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to access user database"
        )


    if not existing_user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )


    # ---------------------------------
    # Verify password
    # ---------------------------------

    try:

        password_valid = verify_password(
            form_data.password,
            existing_user.password_hash
        )

    except Exception:

        logger.exception(
            "Password verification failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to verify password"
        )


    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )


    # ---------------------------------
    # Daily login XP
    # ---------------------------------
    #
    # IMPORTANT:
    # A problem with the optional XP
    # reward should NOT prevent a user
    # from logging into Predix.
    #
    # If XP fails, we log the error
    # and continue with authentication.

    try:

        award_daily_login_xp(
            existing_user,
            db
        )

        db.commit()

    except Exception:

        db.rollback()

        logger.exception(
            "Daily login XP failed for user %s. "
            "Login will continue.",
            existing_user.id
        )


    # ---------------------------------
    # Create JWT
    # ---------------------------------

    try:

        token = create_access_token(
            {
                "user_id": str(existing_user.id)
            }
        )

    except Exception:

        logger.exception(
            "JWT creation failed during login"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create authentication token"
        )


    # ---------------------------------
    # Return authenticated user
    # ---------------------------------

    return {

        "access_token": token,

        "token_type": "bearer",

        "user": {

            "id": str(existing_user.id),

            "username": existing_user.username,

            "email": existing_user.email,

            "country": existing_user.country,

            "role": existing_user.role

        }

    }
```
