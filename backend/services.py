from sqlmodel import Session, select, col
from sqlalchemy import select as sa_select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
import datetime
from typing import Annotated, Optional

from .models import Player, Game, Score, ScoreMethod, GamePublic, PlayerPublic, ScoreCreate, ScorePublic
from .schemas import DailyScoreboardResponse, MonthlyScoreboardResponse
from .stats import calculateDailyCombinedScore, calculateMonthlyPoints
from .exceptions import DuplicateScoreException, InvalidDateException, InvalidUpdateException


def getAllPlayers(session: Session)->list[Player]:
    return list(session.exec(select(Player)).all())

def addNewScore(session: Session, score: ScoreCreate):
    player = session.exec(select(Player).where(Player.name == score.playerName)).first()
    if not player:
        raise HTTPException(404, "Player Not Found")
    assert player.id is not None

    game = session.exec(select(Game).where(Game.name == score.gameName)).first()
    if not game:
        raise HTTPException(404, "Game not found")
    assert game.id is not None

    # check for duplicate score
    existing = session.exec(select(Score).where(Score.playerId == player.id,
                                                Score.gameId == game.id,
                                                Score.date == score.date)
                                                ).first()
    if existing:
        raise DuplicateScoreException(score.playerName,score.gameName,score.date.strftime("%Y-%m-%d"),existing.score)
    
    try:
        db_score = Score(
            date=score.date,
            playerId=player.id,
            gameId=game.id,
            score=score.score)
        session.add(db_score)
        session.commit()
        session.refresh(db_score)
        return {
            "date": db_score.date,
            "playerName": player.name,
            "gameName": game.name,
            "score": db_score.score
        }
    except IntegrityError:
        session.rollback()
        raise DuplicateScoreException(score.playerName,score.gameName,score.date.strftime("%Y-%m-%d"),score.score)
    
def updateScore(session: Session, score: ScoreCreate):
    player = session.exec(select(Player).where(Player.name == score.playerName)).first()
    if not player:
        raise HTTPException(404, "Player Not Found")
    assert player.id is not None

    game = session.exec(select(Game).where(Game.name == score.gameName)).first()
    if not game:
        raise HTTPException(404, "Game not found")
    assert game.id is not None

    # check for duplicate score
    existing = session.exec(select(Score).where(Score.playerId == player.id,
                                                Score.gameId == game.id,
                                                Score.date == score.date)
                                                ).first()
    if existing is None:
        raise InvalidUpdateException()

    existing.score = score.score
    session.add(existing)
    session.commit()
    session.refresh(existing)
    return {
        "date": existing.date,
            "playerName": player.name,
            "gameName": game.name,
            "score": existing.score
    }
def getGamesForPlayer(session: Session, playerName: str) -> list[Game]:
    player = session.exec(select(Player).where(Player.name == playerName)).first()
    if player is None:
        raise HTTPException(status_code=404,detail="Player not found")
    
    return player.games

def getDailyScores(
        session: Session,
        startDate: datetime.date,
        endDate: Optional[datetime.date] = None,
        playerName: Optional[str] = None,
        gameName: Optional[str] = None,) -> list[ScorePublic]:
    query = (
        sa_select(
            col(Score.date),
            col(Game.name).label("gameName"),
            col(Player.name).label("playerName"),
            col(Score.score)
        )
        .select_from(Score)
        .join(Game, col(Score.gameId) == col(Game.id))
        .join(Player, col(Score.playerId) == col(Player.id))
    )
    query = query.where(col(Score.date) >= startDate)
    if endDate:
        query = query.where(col(Score.date) <= endDate)
    if playerName:
        query = query.where(col(Player.name) == playerName)
    if gameName:
        query = query.where(col(Game.name) == gameName)
    results = session.execute(query).all()
    return [ScorePublic.model_validate(result) for result in results]

def getCombinedScores(
        session: Session,
        date: datetime.date
    ) -> list[ScorePublic]:
    # get games info for t_score multiplier
    games = session.exec(select(Game))
    gamesDict = {game.name: game.scoreMethod for game in games}

    # get scores for day
    query = (
        sa_select(
            col(Game.name).label("gameName"),
            col(Player.name).label("playerName"),
            col(Score.score)
        )
        .select_from(Score)
        .join(Game, col(Score.gameId) == col(Game.id))
        .join(Player, col(Score.playerId) == col(Player.id))
    )
    query = query.where(col(Score.date) == date)
    scoreRows = session.execute(query).all()

    if not scoreRows:
        return []
    
    scores = [{"gameName":r.gameName, "playerName": r.playerName, "score": r.score} for r in scoreRows]
    return calculateDailyCombinedScore(gamesDict,scores,date)

def getScoreboardDaily(session: Session,
                       date: datetime.date) -> DailyScoreboardResponse:
    players = session.exec(select(Player)).all()
    games = session.exec(select(Game)).all()

    gamesPublic = [GamePublic.model_validate(game) for game in games]
    gamesPublic.append(
        GamePublic(
            name='Combined',
            scoreMethod=ScoreMethod.HIGH,
            id=0
        )
    )

    gameScores = getDailyScores(session,startDate=date,endDate=date)
    combinedScores = getCombinedScores(session, date=date)

    return DailyScoreboardResponse(
        date=date,
        players=[PlayerPublic.model_validate(player) for player in players],
        games=gamesPublic,
        scores=(gameScores+combinedScores)
    )

def getScoreboardMonthly(session:Session,
                         date: datetime.date) -> MonthlyScoreboardResponse:
    players = session.exec(select(Player)).all()
    games = session.exec(select(Game)).all()

    # Build categories list: participation, individual games, combined, total
    categories = ['Participation', 'Individual', 'Combined', 'Total']
    gameNames = [game.name for game in games]
    # get games info for t_score multiplier
    games = session.exec(select(Game))
    gamesDict = {game.name: game.scoreMethod for game in games}

    startDate = date.replace(day=1)
    endDate = date
    query = (
        sa_select(
            col(Score.date),
            col(Game.name).label("gameName"),
            col(Player.name).label("playerName"),
            col(Score.score)
        )
        .select_from(Score)
        .join(Game, col(Score.gameId) == col(Game.id))
        .join(Player, col(Score.playerId) == col(Player.id))
    )
    query = query.where(col(Score.date) >= startDate).where(col(Score.date) <= endDate)
    scoreRows = session.execute(query).all()

    if not scoreRows:
        raise HTTPException(404, "No scores found for this month")

    scores = [{"date":r.date, "gameName":r.gameName, "playerName": r.playerName, "score": r.score} for r in scoreRows]
    playerPoints = calculateMonthlyPoints(gamesDict,scores)
    return MonthlyScoreboardResponse(
        players=[PlayerPublic.model_validate(player) for player in players],
        categories=categories,
        games=gameNames,
        playerPoints=playerPoints
    )
    
    

    