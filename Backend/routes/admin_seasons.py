from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Season,
    Profile
)

from dependencies import require_admin

from pydantic import BaseModel

from datetime import datetime



router = APIRouter(
    prefix="/admin/seasons",
    tags=["Admin Seasons"]
)





# =====================================
# SCHEMAS
# =====================================


class SeasonCreate(BaseModel):

    name: str

    description: str | None = None

    start_date: datetime

    end_date: datetime

    reward_rules: list





class SeasonUpdate(BaseModel):

    name: str | None = None

    description: str | None = None

    start_date: datetime | None = None

    end_date: datetime | None = None

    status: str | None = None

    reward_rules: list | None = None





# =====================================
# CREATE SEASON
# =====================================


@router.post("")
def create_season(

    data: SeasonCreate,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    season = Season(

        name=data.name,

        description=data.description,

        start_date=data.start_date,

        end_date=data.end_date,

        reward_rules=data.reward_rules,

        status="UPCOMING"

    )


    db.add(season)

    db.commit()

    db.refresh(season)



    return {

        "message":"Season created successfully",

        "season":season

    }





# =====================================
# GET ALL SEASONS
# =====================================


@router.get("")
def get_seasons(

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    seasons = db.query(
        Season
    ).order_by(
        Season.created_at.desc()
    ).all()



    return seasons





# =====================================
# GET SINGLE SEASON
# =====================================


@router.get("/{season_id}")
def get_season(

    season_id:str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):


    season = db.query(
        Season
    ).filter(
        Season.id == season_id
    ).first()



    if not season:

        raise HTTPException(

            status_code=404,

            detail="Season not found"

        )



    return season





# =====================================
# UPDATE SEASON
# =====================================


@router.put("/{season_id}")
def update_season(

    season_id:str,

    data:SeasonUpdate,

    db:Session = Depends(get_db),

    admin:Profile = Depends(require_admin)

):


    season = db.query(
        Season
    ).filter(
        Season.id == season_id
    ).first()



    if not season:

        raise HTTPException(

            status_code=404,

            detail="Season not found"

        )



    for key,value in data.dict(
        exclude_unset=True
    ).items():

        setattr(
            season,
            key,
            value
        )



    db.commit()

    db.refresh(season)



    return {

        "message":"Season updated successfully",

        "season":season

    }





# =====================================
# DELETE SEASON
# =====================================


@router.delete("/{season_id}")
def delete_season(

    season_id:str,

    db:Session = Depends(get_db),

    admin:Profile = Depends(require_admin)

):


    season = db.query(
        Season
    ).filter(
        Season.id == season_id
    ).first()



    if not season:

        raise HTTPException(

            status_code=404,

            detail="Season not found"

        )



    db.delete(season)

    db.commit()



    return {

        "message":"Season deleted successfully"

    }
    
# =====================================
# ACTIVATE SEASON
# =====================================

@router.put("/{season_id}/activate")
def activate_season(

    season_id: str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):

    season = db.query(
        Season
    ).filter(
        Season.id == season_id
    ).first()


    if not season:

        raise HTTPException(
            status_code=404,
            detail="Season not found"
        )


    if season.status == "ENDED":

        raise HTTPException(
            status_code=400,
            detail="Season already ended"
        )


    season.status = "ACTIVE"


    db.commit()

    db.refresh(season)


    return {

        "message":"Season activated successfully",

        "season":season.name,

        "status":season.status

    }
    
# =====================================
# END SEASON
# =====================================

@router.put("/{season_id}/end")
def end_season(

    season_id: str,

    db: Session = Depends(get_db),

    admin: Profile = Depends(require_admin)

):

    season = db.query(
        Season
    ).filter(
        Season.id == season_id
    ).first()


    if not season:

        raise HTTPException(
            status_code=404,
            detail="Season not found"
        )


    if season.status == "ENDED":

        raise HTTPException(
            status_code=400,
            detail="Season already ended"
        )


    season.status = "ENDED"


    db.commit()

    db.refresh(season)


    return {

        "message": "Season ended successfully",

        "season": season.name,

        "status": season.status

    }