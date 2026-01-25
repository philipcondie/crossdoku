from sqlmodel import SQLModel
from .models import GamePublic, PlayerPublic
import datetime

class GamesResponse(SQLModel):
    games: list[GamePublic]

class ScoreCreate(SQLModel):
    date: datetime.date
    playerName: str
    gameName: str
    score: int

class ScoreResponse(SQLModel):
    date: datetime.date
    playerName: str
    gameName: str
    score: int

class DailyScoreboardResponse(SQLModel):
    date: datetime.date
    players: list[PlayerPublic]
    games: list[GamePublic]
    scores: list[ScoreResponse]

class PlayerMonthlyPoint(SQLModel):
    playerName: str
    category: str
    points: int

class MonthlyScoreboardResponse(SQLModel):
    players: list[PlayerPublic]
    categories: list[str]
    games: list[str]
    playerPoints: list[PlayerMonthlyPoint] 
