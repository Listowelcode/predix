from datetime import datetime, timedelta

from jose import jwt

from passlib.context import CryptContext

from dotenv import load_dotenv

import os



load_dotenv()



SECRET_KEY = os.getenv(
    "SECRET_KEY"
)


ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)



if not SECRET_KEY:

    raise Exception(
        "SECRET_KEY missing in .env"
    )



ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24





pwd_context = CryptContext(

    schemes=["bcrypt"],

    deprecated="auto"

)





# ==============================
# PASSWORD HASHING
# ==============================

def hash_password(password: str):


    # bcrypt only supports 72 bytes

    password = password[:72]


    return pwd_context.hash(password)







def verify_password(

    plain_password,

    hashed_password

):


    plain_password = plain_password[:72]


    return pwd_context.verify(

        plain_password,

        hashed_password

    )








# ==============================
# JWT TOKEN
# ==============================

def create_access_token(

    data: dict

):


    to_encode = data.copy()



    expire = datetime.utcnow() + timedelta(

        minutes=ACCESS_TOKEN_EXPIRE_MINUTES

    )



    to_encode.update(

        {

            "exp": expire

        }

    )



    token = jwt.encode(

        to_encode,

        SECRET_KEY,

        algorithm=ALGORITHM

    )



    return token