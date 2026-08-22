import logging

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from fastapi.middleware.gzip import GZipMiddleware


from database import engine, SessionLocal

from models import Base

from services.seed import ensure_match_schema, ensure_decimal_points_schema, ensure_badge_schema, seed_badges


logging.basicConfig(level=logging.INFO)



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
from routes import admin_badges




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


app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:5500",

        "http://127.0.0.1:5500",

        "http://localhost:5501",

        "http://127.0.0.1:5501",

        "http://localhost:3000",

        "http://127.0.0.1:3000",

        "http://localhost:5173",

        "http://127.0.0.1:5173",

        "http://localhost:8080",

        "http://127.0.0.1:8080",

        # Opening the html files directly (double-click) sends
        # Origin: null — allow that too so the app still works
        # without a local dev server.
        "null"

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)



# Compresses every response over ~1KB (JSON payloads like
# /matches, /tickets/my, /leaderboard, etc.) before it goes over
# the wire — smaller payload, faster fetch on the frontend, with
# zero changes needed on the client (fetch() decompresses
# automatically).
app.add_middleware(

    GZipMiddleware,

    minimum_size=1000

)







# ===============================
# DATABASE
# ===============================


Base.metadata.create_all(

    bind=engine

)

# Existing databases do not get new model columns from create_all();
# repair the match schema before any startup code queries Match rows.
ensure_match_schema(engine)
ensure_decimal_points_schema(engine)


# ===============================
# BADGES — SCHEMA + SEED
# ===============================
# Ensures the `badges` table has the `rarity` column (needed on
# databases that already had this table before rarity existed),
# then makes sure every badge in the catalog exists in Supabase.
# Runs on every startup so this always self-heals — no manual
# SQL required. If this ever fails (e.g. bad DATABASE_URL,
# permissions), it's logged loudly instead of crashing the whole
# API — check the server logs, or hit
# POST /admin/badges/reseed to retry manually.

ensure_badge_schema(engine)

_seed_db = SessionLocal()

try:

    result = seed_badges(_seed_db)

    logging.getLogger("predix.startup").info(
        f"Badge seed complete: {result}"
    )

except Exception as exc:

    logging.getLogger("predix.startup").error(
        f"Badge seed FAILED on startup: {exc}"
    )

finally:
    _seed_db.close()







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


app.include_router(
    admin_badges.router
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