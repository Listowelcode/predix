from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware


from database import engine

from models import Base



# ===============================
# ROUTES
# ===============================

from routes import auth
from routes import matches
from routes import predictions
from routes import tickets
from routes import players
from routes import profile
from routes import results
from routes import leaderboard


# ADMIN ROUTES

from routes import admin_dashboard
from routes import admin_matches
from routes import admin_users
from routes import admin_seasons
from routes import admin_season_rewards
from routes import admin_tickets




# ===============================
# APP
# ===============================


app = FastAPI(

    title="Predix API",

    version="1.0.0"

)






# ===============================
# CORS
# ===============================


from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "*"
    ],

    allow_credentials=False,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)






# ===============================
# DATABASE
# ===============================


Base.metadata.create_all(

    bind=engine

)







# ===============================
# ROUTERS
# ===============================


app.include_router(
    auth.router
)


app.include_router(
    matches.router
)


app.include_router(
    predictions.router
)


app.include_router(
    tickets.router
)


app.include_router(
    players.router
)


app.include_router(
    profile.router
)


app.include_router(
    results.router
)


app.include_router(
    leaderboard.router
)

app.include_router(
    admin_tickets.router
)





# ADMIN


app.include_router(
    admin_dashboard.router
)


app.include_router(
    admin_matches.router
)


app.include_router(
    admin_users.router
)


app.include_router(
    admin_seasons.router
)


app.include_router(
    admin_season_rewards.router
)








# ===============================
# TEST ROUTES
# ===============================


@app.get("/")
def home():

    return {

        "message":
        "Predix Backend Running 🚀"

    }





@app.get("/health")
def health():

    return {

        "status":
        "healthy"

    }
