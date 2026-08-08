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

    # Full international phone number, e.g. "+233241234567"
    # (dial code from the country selector + the digits the user typed).
    phone: str = Field(
        min_length=7,
        max_length=20
    )

    # ISO 3166-1 alpha-2 country code from the signup country/flag
    # selector, e.g. "GH". Drives the flag shown on the leaderboard.
    country: str = Field(
        min_length=2,
        max_length=2
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

    phone: Optional[str] = None

    country: Optional[str] = None

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

    # Minutes the match should be treated as LIVE for, starting at
    # match_date. Defaults to a standard 90 minute football match.
    duration_minutes: int = 90


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

    duration_minutes: int = 90

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

    duration_minutes: Optional[int] = None

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
    
