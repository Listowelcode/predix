from pydantic import BaseModel, EmailStr, Field

from typing import Optional

from datetime import datetime

from uuid import UUID



# ==========================================
# AUTH SCHEMAS
# ==========================================

class RegisterRequest(BaseModel):

    username: str

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=72
    )



class LoginRequest(BaseModel):

    email: EmailStr

    password: str





# ==========================================
# PROFILE SCHEMAS
# ==========================================


class ProfileResponse(BaseModel):

    id: UUID

    username: str

    email: str

    avatar_url: Optional[str] = None

    points: int

    xp: int

    tickets: int

    level: int

    wins: int

    losses: int

    draws: int

    role: str

    created_at: datetime
    
    current_streak: int

    best_streak: int



    class Config:

        from_attributes = True







# ==========================================
# MATCH SCHEMAS
# ==========================================

class MatchCreate(BaseModel):

    home_team: str

    away_team: str

    league: Optional[str] = None

    match_date: datetime

    kickoff_time: Optional[str] = None


    home_win_points: int = 0

    away_win_points: int = 0

    draw_points: int = 0




class MatchResponse(BaseModel):

    id: UUID

    home_team: str

    away_team: str

    home_logo: Optional[str] = None

    away_logo: Optional[str] = None

    league: Optional[str] = None

    match_date: datetime

    kickoff_time: Optional[str] = None

    home_score: Optional[int] = None

    away_score: Optional[int] = None
    
    home_win_points: int

    away_win_points: int

    draw_points: int

    winner: Optional[str] = None

    status: str



    class Config:

        from_attributes = True




class MatchUpdate(BaseModel):

    home_team: Optional[str] = None

    away_team: Optional[str] = None

    league: Optional[str] = None

    match_date: Optional[datetime] = None

    kickoff_time: Optional[str] = None

    home_win_points: Optional[int] = None

    away_win_points: Optional[int] = None

    draw_points: Optional[int] = None


# ==========================================
# PREDICTION SCHEMAS
# ==========================================


class PredictionCreate(BaseModel):

    match_id: UUID

    prediction: str



class PredictionResponse(BaseModel):

    id: UUID

    match_id: UUID

    prediction: str

    status: str

    points_won: int

    created_at: datetime


    class Config:

        from_attributes = True
    
