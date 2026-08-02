from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON, Text

from sqlalchemy.dialects.postgresql import UUID
from database import Base
from sqlalchemy.orm import relationship
import uuid

from datetime import datetime





# ==========================================
# USER PROFILE
# ==========================================

class Profile(Base):

    __tablename__ = "profiles"


    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


    username = Column(
        String,
        unique=True,
        nullable=False
    )


    email = Column(
        String,
        unique=True,
        nullable=False
    )


    password_hash = Column(
        String,
        nullable=False
    )


    avatar_url = Column(
        String,
        nullable=True
    )



    # =========================
    # GAME DATA
    # =========================

    points = Column(
        Integer,
        default=0
    )


    xp = Column(
        Integer,
        default=0
    )


    tickets = Column(
        Integer,
        default=5
    )


    level = Column(
        Integer,
        default=1
    )


    wins = Column(
        Integer,
        default=0
    )


    losses = Column(
        Integer,
        default=0
    )


    draws = Column(
        Integer,
        default=0
    )



    # =========================
    # ACCOUNT
    # =========================

    role = Column(
        String,
        default="USER"
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )



    # =========================
    # PREDICTIONS
    # =========================

    predictions = relationship(

        "Prediction",

        back_populates="user",

        cascade="all, delete-orphan"

    )



    # =========================
    # TICKETS
    # =========================

    prediction_tickets = relationship(

        "PredictionTicket",

        back_populates="user",

        cascade="all, delete-orphan"

    )



    # =========================
    # TICKET HISTORY
    # =========================

    ticket_history = relationship(

        "TicketHistory",

        back_populates="user",

        cascade="all, delete-orphan"

    )



    # =========================
    # BADGES
    # =========================

    badges = relationship(

        "UserBadge",

        back_populates="user",

        cascade="all, delete-orphan"

    )



    # =========================
    # STREAK SYSTEM
    # =========================

    current_streak = Column(

        Integer,

        default=0

    )


    best_streak = Column(

        Integer,

        default=0

    )

# ==========================================
# FOOTBALL MATCHES
# ==========================================

class Match(Base):

    __tablename__ = "matches"



    id = Column(

        UUID(as_uuid=True),

        primary_key=True,

        default=uuid.uuid4

    )



    home_team = Column(

        String,

        nullable=False

    )



    away_team = Column(

        String,

        nullable=False

    )



    home_logo = Column(

        String,

        nullable=True

    )



    away_logo = Column(

        String,

        nullable=True

    )



    league = Column(

        String,

        nullable=True

    )



    match_date = Column(

        DateTime,

        nullable=False

    )



    kickoff_time = Column(

        String,

        nullable=True

    )



    home_score = Column(

        Integer,

        nullable=True

    )



    away_score = Column(

        Integer,

        nullable=True

    )



    # HOME_WIN / AWAY_WIN / DRAW

    winner = Column(

        String,

        nullable=True

    )



    # UPCOMING / LIVE / FINISHED

    status = Column(

        String,

        default="UPCOMING",

        nullable=False

    )



    home_win_points = Column(

        Integer,

        default=0

    )



    away_win_points = Column(

        Integer,

        default=0

    )



    draw_points = Column(

        Integer,

        default=0

    )



    created_at = Column(

        DateTime,

        default=datetime.utcnow

    )



    # =========================
    # RELATIONSHIPS
    # =========================


    predictions = relationship(

        "Prediction",

        back_populates="match",

        cascade="all, delete-orphan"

    )
# ==========================================
# USER PREDICTIONS
# ==========================================
# ==========================================
# USER PREDICTIONS
# ==========================================

class Prediction(Base):

    __tablename__ = "predictions"



    id = Column(

        UUID(as_uuid=True),

        primary_key=True,

        default=uuid.uuid4

    )



    # =========================
    # USER
    # =========================

    user_id = Column(

        UUID(as_uuid=True),

        ForeignKey("profiles.id"),

        nullable=False

    )



    # =========================
    # MATCH
    # =========================

    match_id = Column(

        UUID(as_uuid=True),

        ForeignKey("matches.id"),

        nullable=False

    )



    # =========================
    # TICKET
    # =========================

    ticket_id = Column(

        UUID(as_uuid=True),

        ForeignKey("prediction_tickets.id"),

        nullable=False

    )



    # =========================
    # PREDICTION DATA
    # =========================

    prediction = Column(

        String,

        nullable=False

    )


    status = Column(

        String,

        default="PENDING"

    )


    points_won = Column(

        Integer,

        default=0

    )


    created_at = Column(

        DateTime,

        default=datetime.utcnow

    )



    # =========================
    # RELATIONSHIPS
    # =========================


    user = relationship(

        "Profile",

        back_populates="predictions"

    )



    match = relationship(

        "Match",

        back_populates="predictions"

    )



    ticket = relationship(

        "PredictionTicket",

        back_populates="predictions"

    )
# ==========================================
# TICKET HISTORY
# ==========================================

class TicketHistory(Base):

    __tablename__ = "ticket_history"



    id = Column(

        UUID(as_uuid=True),

        primary_key=True,

        default=uuid.uuid4

    )



    user_id = Column(

        UUID(as_uuid=True),

        ForeignKey(
            "profiles.id",
            ondelete="CASCADE"
        ),

        nullable=False

    )



    amount = Column(

        Integer,

        nullable=False

    )



    # USED / EARNED / PURCHASED

    action = Column(

        String,

        nullable=False

    )



    created_at = Column(

        DateTime,

        default=datetime.utcnow

    )



    user = relationship(

        "Profile",

        back_populates="ticket_history"

    )
# ==========================================
# PREDICTION TICKETS
# ==========================================

class PredictionTicket(Base):

    __tablename__ = "prediction_tickets"



    id = Column(

        UUID(as_uuid=True),

        primary_key=True,

        default=uuid.uuid4

    )



    user_id = Column(

        UUID(as_uuid=True),

        ForeignKey("profiles.id"),

        nullable=False

    )



    ticket_number = Column(

        String,

        unique=True,

        nullable=False

    )



    total_matches = Column(

        Integer,

        nullable=False

    )



    # Maximum possible points from this ticket

    possible_points = Column(

        Integer,

        default=0

    )



    # Actual points after matches finish

    points_won = Column(

        Integer,

        default=0

    )



    # PENDING / WON / LOST

    status = Column(

        String,

        default="PENDING"

    )



    created_at = Column(

        DateTime,

        default=datetime.utcnow

    )



    # =========================
    # USER RELATION
    # =========================

    user = relationship(

        "Profile",

        back_populates="prediction_tickets"

    )



    # =========================
    # PREDICTION RELATION
    # =========================

    predictions = relationship(

        "Prediction",

        back_populates="ticket",

        cascade="all, delete-orphan"

    )
# ==========================================
# POINTS HISTORY
# ==========================================

class PointsHistory(Base):

    __tablename__ = "points_history"


    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


    user_id = Column(
        UUID,
        ForeignKey("profiles.id"),
        nullable=False
    )


    points = Column(
        Integer,
        nullable=False
    )


    reason = Column(
        String,
        nullable=False
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )








# ==========================================
# LEADERBOARD
# ==========================================

class Leaderboard(Base):

    __tablename__ = "leaderboards"


    id = Column(
        UUID(as_uuid=True),
        primary_key = True,
        default=uuid.uuid4
    )


    user_id = Column(
        UUID,
        ForeignKey("profiles.id"),
        nullable=False
    )


    total_points = Column(
        Integer,
        default=0
    )


    wins = Column(
        Integer,
        default=0
    )


    losses = Column(
        Integer,
        default=0
    )


    draws = Column(
        Integer,
        default=0
    )


    updated_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    
    
class Badge(Base):

    __tablename__ = "badges"

    id = Column(UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4)

    name = Column(String, unique=True)

    description = Column(Text)

    icon = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )



class UserBadge(Base):

    __tablename__ = "user_badges"

    id = Column(UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4)

    user_id = Column(
        UUID,
        ForeignKey("profiles.id")
    )

    badge_id = Column(
        UUID,
        ForeignKey("badges.id")
    )

    earned_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
    "Profile",
    back_populates="badges"
)

    badge = relationship(
        "Badge"
    )

    badge = relationship("Badge")
    
class League(Base):

    __tablename__ = "leagues"


    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


    name = Column(
        String,
        nullable=False
    )


    country = Column(
        String,
        nullable=True
    )


    logo = Column(
        String,
        nullable=True
    )


    status = Column(
        String,
        default="ACTIVE"
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    
    
class Season(Base):

    __tablename__ = "seasons"


    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


    name = Column(
        String,
        nullable=False
    )


    description = Column(
        Text
    )


    start_date = Column(
        DateTime,
        nullable=False
    )


    end_date = Column(
        DateTime,
        nullable=False
    )


    status = Column(
        String,
        default="UPCOMING"
    )


    reward_rules = Column(
        JSON
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    
class SeasonReward(Base):

    __tablename__ = "season_rewards"


    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


    season_id = Column(
        UUID(as_uuid=True),
        ForeignKey("seasons.id"),
        nullable=False
    )


    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=False
    )


    points_at_end = Column(
        Integer,
        nullable=False
    )


    tickets_awarded = Column(
        Integer,
        default=0
    )


    claimed = Column(
        Boolean,
        default=False
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )