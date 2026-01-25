from typing import List
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
import datetime
from enum import Enum

### Link Table for Player-Game many-to-many relationship

class PlayerGameLink(SQLModel, table=True):
    player_id: int | None = Field(default=None, foreign_key="player.id", primary_key=True, ondelete="CASCADE")
    game_id: int | None = Field(default=None, foreign_key="game.id", primary_key=True, ondelete="CASCADE")

### Player Models

class PlayerBase(SQLModel):
    name: str

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase,table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    games: List["Game"] = Relationship(back_populates="players", link_model=PlayerGameLink)
    scores: List["Score"] = Relationship(back_populates="player", cascade_delete=True)

class PlayerPublic(PlayerBase):
    id: int

### Game Models

class ScoreMethod (int, Enum):
    # this is needed to select winners and adjust t-scores appropriately based on if the winner is the highest or lowest value
    HIGH = 100
    LOW = -100

class GameBase(SQLModel):
    name: str
    scoreMethod: ScoreMethod

class GameCreate(GameBase):
    pass

class Game(GameBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    players: List["Player"] = Relationship(back_populates="games", link_model=PlayerGameLink)
    scores: List["Score"] = Relationship(back_populates="game", cascade_delete=True)

class GamePublic(GameBase):
    id: int

### Score Models

class ScoreBase(SQLModel):
    date: datetime.date
    playerId: int
    gameId: int
    score: int


class Score(ScoreBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime.date
    playerId: int = Field(foreign_key="player.id", ondelete="CASCADE")
    gameId: int = Field(foreign_key="game.id", ondelete="CASCADE")
    score: int = Field(ge=0)

    __table_args__ = (
        UniqueConstraint("playerId","gameId","date", name="uq_player_game_date"),
    )

    player: Player = Relationship(back_populates="scores")
    game: Game = Relationship(back_populates="scores")

class ScorePublic(ScoreBase):
    id: int

# Add models for: 
#   responses with relationships
#   update models