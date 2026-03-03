from typing import List
from sqlalchemy import UniqueConstraint, Table, Column, ForeignKey, Date, CheckConstraint, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
from enum import IntEnum

class Base(DeclarativeBase):
    pass

### Link Table for Player-Game many-to-many relationship

player_game_table = Table(
    "player_game_link",
    Base.metadata,
    Column("player_id", ForeignKey("players.id",ondelete="CASCADE"),primary_key=True),
    Column("game_id", ForeignKey("games.id",ondelete="CASCADE"),primary_key=True)
)



class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    games: Mapped[List["Game"]] = relationship(secondary=player_game_table,back_populates="players")
    scores: Mapped[List["Score"]] = relationship(back_populates="player",cascade="all, delete-orphan", passive_deletes=True)

### Game Models

class ScoreMethod(IntEnum):
    # this is needed to select winners and adjust t-scores appropriately based on if the winner is the highest or lowest value
    HIGH = 100
    LOW = -100

class Game(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    scoreMethod: Mapped[ScoreMethod] = mapped_column(Integer)

    players: Mapped[List["Player"]] = relationship(secondary=player_game_table,back_populates="games")
    scores: Mapped[List["Score"]] = relationship(back_populates="game",cascade="all, delete-orphan", passive_deletes=True)

class Score(Base):
    __tablename__ = "scores"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date)
    playerId: Mapped[int] = mapped_column(ForeignKey("players.id",ondelete="CASCADE"))
    gameId: Mapped[int] = mapped_column(ForeignKey("games.id",ondelete="CASCADE"))
    score: Mapped[int] = mapped_column(CheckConstraint('score >= 0',name='min_score_check'))

    __table_args__ = (
        UniqueConstraint("playerId","gameId","date", name="uq_player_game_date"),
    )

    player: Mapped[Player] = relationship(back_populates="scores")
    game: Mapped[Game] = relationship(back_populates="scores")

