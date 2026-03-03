from pydantic import BaseModel, ConfigDict
from .models import ScoreMethod
import datetime

### Player Models

class PlayerBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str

class PlayerCreate(PlayerBase):
    pass

class PlayerPublic(PlayerBase):
    id: int

class GameBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    scoreMethod: ScoreMethod

class GameCreate(GameBase):
    pass

class GamePublic(GameBase):
    id: int

### Score Models
class ScoreBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    date: datetime.date
    score: int

class ScorePublic(ScoreBase):
    playerName: str
    gameName: str

class ScoreCreate(ScoreBase):
    playerName: str
    gameName: str

class AuthRequest(BaseModel):
    password: str

class DailyScoreboardResponse(BaseModel):
    date: datetime.date
    players: list[PlayerPublic]
    games: list[GamePublic]
    scores: list[ScorePublic]

class PlayerMonthlyPoint(BaseModel):
    playerName: str
    category: str
    points: int

class MonthlyScoreboardResponse(BaseModel):
    players: list[PlayerPublic]
    categories: list[str]
    games: list[str]
    playerPoints: list[PlayerMonthlyPoint] 
    