from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    League,
    Profile
)

from dependencies import require_admin

from pydantic import BaseModel



router = APIRouter(
    prefix="/admin/leagues",
    tags=["Admin Leagues"]
)





# ================================
# SCHEMAS
# ================================


class LeagueCreate(BaseModel):

    name: str

    country: str | None = None

    logo: str | None = None





class LeagueUpdate(BaseModel):

    name: str | None = None

    country: str | None = None

    logo: str | None = None

    status: str | None = None





# ================================
# GET ALL LEAGUES
# ================================


@router.get("")
def get_leagues(

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    return db.query(
        League
    ).all()





# ================================
# CREATE LEAGUE
# ================================


@router.post("")
def create_league(

    data: LeagueCreate,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    league = League(

        name=data.name,

        country=data.country,

        logo=data.logo

    )


    db.add(league)

    db.commit()

    db.refresh(league)



    return {

        "message": "League created successfully",

        "league": league

    }





# ================================
# UPDATE LEAGUE
# ================================


@router.put("/{league_id}")
def update_league(

    league_id: str,

    data: LeagueUpdate,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    league = db.query(
        League
    ).filter(
        League.id == league_id
    ).first()



    if not league:

        raise HTTPException(
            404,
            "League not found"
        )



    for key,value in data.dict(
        exclude_unset=True
    ).items():

        setattr(
            league,
            key,
            value
        )



    db.commit()

    db.refresh(league)



    return {

        "message": "League updated successfully",

        "league": league

    }





# ================================
# DELETE LEAGUE
# ================================


@router.delete("/{league_id}")
def delete_league(

    league_id: str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    league = db.query(
        League
    ).filter(
        League.id == league_id
    ).first()



    if not league:

        raise HTTPException(
            404,
            "League not found"
        )



    db.delete(league)

    db.commit()



    return {

        "message": "League deleted successfully"

    }