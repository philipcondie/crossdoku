from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
import datetime
from typing import Optional

from .models import Player, Game, Score, ScoreMethod
from .schemas import DailyScoreboardResponse, MonthlyScoreboardResponse, GamePublic, PlayerPublic, ScoreCreate, ScorePublic
from .stats import calculateDailyCombinedScore, calculateMonthlyPoints
from .exceptions import DuplicateScoreException, InvalidUpdateException


def getAllPlayers(session: Session)->list[Player]:
    return list(session.scalars(select(Player)).all())

def addNewScore(session: Session, score: ScoreCreate):
    player = session.scalars(select(Player).where(Player.name == score.playerName)).one_or_none()
    if not player:
        raise HTTPException(404, "Player Not Found")

    game = session.scalars(select(Game).where(Game.name == score.gameName)).one_or_none()
    if not game:
        raise HTTPException(404, "Game not found")

    # check for duplicate score
    existing = session.scalars(select(Score).where(Score.playerId == player.id,
                                                Score.gameId == game.id,
                                                Score.date == score.date)
                                                ).one_or_none()
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
    player = session.scalars(select(Player).where(Player.name == score.playerName)).one_or_none()
    if not player:
        raise HTTPException(404, "Player Not Found")

    game = session.scalars(select(Game).where(Game.name == score.gameName)).one_or_none()
    if not game:
        raise HTTPException(404, "Game not found")

    # check for duplicate score
    existing = session.scalars(select(Score).where(Score.playerId == player.id,
                                                Score.gameId == game.id,
                                                Score.date == score.date)
                                                ).one_or_none()
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
    player = session.scalars(select(Player).where(Player.name == playerName)).one_or_none()
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
        select(
            Score.date,
            Game.name.label("gameName"),
            Player.name.label("playerName"),
            Score.score
        )
        .select_from(Score)
        .join(Game, Score.gameId == Game.id)
        .join(Player, Score.playerId == Player.id)
    )
    query = query.where(Score.date >= startDate)
    if endDate:
        query = query.where(Score.date <= endDate)
    if playerName:
        query = query.where(Player.name == playerName)
    if gameName:
        query = query.where(Game.name == gameName)
    results = session.execute(query).mappings().all()
    return [ScorePublic.model_validate(result) for result in results]

def getCombinedScores(
        session: Session,
        date: datetime.date
    ) -> list[ScorePublic]:
    # get games info for t_score multiplier
    gameRows = session.scalars(select(Game))
    gamesDict = {game.name: game.scoreMethod for game in gameRows}

    # get scores for day
    query = (
        select(
            Game.name.label("gameName"),
            Player.name.label("playerName"),
            Score.score
        )
        .select_from(Score)
        .join(Game, Score.gameId == Game.id)
        .join(Player, Score.playerId == Player.id)
    )
    query = query.where(Score.date == date)
    scoreRows = session.execute(query).mappings().all()

    if not scoreRows:
        return []
    
    scores = [{"gameName":r.gameName, "playerName": r.playerName, "score": r.score} for r in scoreRows]
    return calculateDailyCombinedScore(gamesDict,scores,date)

def getScoreboardDaily(session: Session,
                       date: datetime.date) -> DailyScoreboardResponse:
    players = session.scalars(select(Player)).all()
    games = session.scalars(select(Game)).all()

    gamesPublic = [GamePublic.model_validate(game) for game in games]

    gameScores = getDailyScores(session,startDate=date,endDate=date)
    sortedGameScores = []

    for game in gamesPublic:
        filteredScores = [score for score in gameScores if score.gameName == game.name]
        order = False
        if game.scoreMethod == ScoreMethod.HIGH:
            order = True
        sortedScores = sorted(filteredScores, key= lambda s: s.score, reverse=order)
        sortedGameScores.extend(sortedScores)

    combinedScores = getCombinedScores(session, date=date)
    sortedCombined = sorted(combinedScores, key= lambda s: s.score, reverse=True)

    gamesPublic.append(
        GamePublic(
            name='Combined',
            scoreMethod=ScoreMethod.HIGH,
            id=0
        )
    )

    return DailyScoreboardResponse(
        date=date,
        players=[PlayerPublic.model_validate(player) for player in players],
        games=gamesPublic,
        scores=(sortedCombined + sortedGameScores)
    )

def getScoreboardMonthly(session:Session,
                         date: datetime.date) -> MonthlyScoreboardResponse:
    players = session.scalars(select(Player)).all()
    games = session.scalars(select(Game)).all()

    # Build categories list: participation, individual games, combined, total
    categories = ['Participation', 'Individual', 'Combined', 'Total']
    gameNames = [game.name for game in games]
    gamesDict = {game.name: game.scoreMethod for game in games}

    startDate = date.replace(day=1)
    endDate = date
    query = (
        select(
            Score.date,
            Game.name.label("gameName"),
            Player.name.label("playerName"),
            Score.score
        )
        .select_from(Score)
        .join(Game, Score.gameId == Game.id)
        .join(Player, Score.playerId == Player.id)
    )
    query = query.where(Score.date >= startDate).where(Score.date <= endDate)
    scoreRows = session.execute(query).mappings().all()

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
    
    

    
