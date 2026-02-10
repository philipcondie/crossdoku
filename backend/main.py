from typing import Annotated, Optional
import datetime
from zoneinfo import ZoneInfo
from sqlmodel import Session, select, col
from sqlalchemy import select as sa_select
from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .models import PlayerPublic, GamePublic, ScorePublic, ScoreCreate
from .schemas import DailyScoreboardResponse, MonthlyScoreboardResponse, AuthRequest
from .database import get_session, create_db_and_tables, close_db, seed_database
from .exceptions import InvalidPasswordException, InvalidDateException
from .services import getAllPlayers, addNewScore, getGamesForPlayer, getDailyScores, getCombinedScores, getScoreboardDaily, getScoreboardMonthly, updateScore as updateScoreService
from .config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # start up operations
    create_db_and_tables()
    seed_database()
    yield
    # shut down operations
    close_db()

SessionDep = Annotated[Session,Depends(get_session)]

EASTERN = ZoneInfo("America/New_York")

def max_allowed_date() -> datetime.date:
    """Return the latest date a score can be submitted for,
    accounting for early puzzle release times.

    - Sunday puzzles release at 6 PM Eastern on Saturday
    - Mon-Sat puzzles release at 10 PM Eastern the night before
    """
    now = datetime.datetime.now(EASTERN)
    today = now.date()
    tomorrow = today + datetime.timedelta(days=1)
    if tomorrow.weekday() == 6 and now.hour >= 18:
        return tomorrow
    elif now.hour >= 22:
        return tomorrow

    return today

app = FastAPI(lifespan=lifespan)
settings = get_settings()

origins = settings.cors_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.post("/auth/verify")
def verify_password(request: AuthRequest):
    if request.password != settings.app_password:
        raise InvalidPasswordException()
    return {"authenticated": True}

@app.get("/players/", response_model=list[PlayerPublic])
def getPlayers(
    session: SessionDep
    ):
    return getAllPlayers(session=session)

@app.post("/score/", response_model=ScorePublic)
def addScore(
    session: SessionDep,
    score: ScoreCreate
    ):
    if score.date > max_allowed_date():
        raise InvalidDateException()
    
    return addNewScore(session, score)

@app.put("/score/", response_model=ScorePublic)
def updateScore(
    session: SessionDep,
    score: ScoreCreate
):
    return updateScoreService(session, score)
    
@app.get("/games/{playerName}", response_model=list[GamePublic])
def getGames(
    session: SessionDep,
    playerName: str):
   return getGamesForPlayer(session, playerName)
    
@app.get("/scores/", response_model=list[ScorePublic])
def getScores(
    session: SessionDep,
    startDate: datetime.date,
    endDate: Optional[datetime.date] = None,
    playerName: Optional[str] = None,
    gameName: Optional[str] = None,
):
    if startDate > max_allowed_date():
        raise InvalidDateException()
    if endDate and endDate > max_allowed_date():
        raise InvalidDateException()
    return getDailyScores(session,startDate,endDate,playerName,gameName)
    
@app.get("/scores/combined", response_model=list[ScorePublic])
def getCombinedScores(
    session: SessionDep,
    date: datetime.date
):
    if date > max_allowed_date():
        raise InvalidDateException()
    return getCombinedScores(session,date)

@app.get("/scores/daily", response_model=DailyScoreboardResponse)
def getDailyScoreboard(
    session: SessionDep,
    date: datetime.date
):
    if date > max_allowed_date():
        raise InvalidDateException()
    return getScoreboardDaily(session, date)

@app.get("/scores/monthly", response_model=MonthlyScoreboardResponse)
def getMonthlyScoreboard(
    session: SessionDep,
    date: datetime.date
):
    if date > max_allowed_date():
        raise InvalidDateException()
    return getScoreboardMonthly(session,date) 