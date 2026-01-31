from sqlmodel import SQLModel
from .models import GamePublic, PlayerPublic, ScorePublic
import datetime

class DailyScoreboardResponse(SQLModel):
    date: datetime.date
    players: list[PlayerPublic]
    games: list[GamePublic]
    scores: list[ScorePublic]

class PlayerMonthlyPoint(SQLModel):
    playerName: str
    category: str
    points: int

class MonthlyScoreboardResponse(SQLModel):
    players: list[PlayerPublic]
    categories: list[str]
    games: list[str]
    playerPoints: list[PlayerMonthlyPoint] 
