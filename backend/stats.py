from sqlmodel import Session, col, select
from sqlalchemy import select as sa_select
import datetime
import pandas as pd
import numpy as np
from typing import Any

from .models import ScorePublic
from .schemas import PlayerMonthlyPoint

def _compute_t_scores(scores: pd.DataFrame) -> pd.DataFrame:
    gameStats = scores.groupby(['date','gameName']).agg({'score':['mean','std']}).reset_index()
    gameStats.columns = ['date', 'gameName', 'mean', 'std']

    scores = scores.merge(gameStats,on=['date','gameName'],how='left')
    
    scores['t_score'] = np.where(
        (scores['std'] == 0) | (scores['std'].isna()),
        0, # if only one player has played this will prevent divide by 0 errors
        (scores['score'] - scores['mean']) / scores['std'] * scores['t_multiplier']
        )
    return scores

def _compute_individual_game_points(scores: pd.DataFrame, gameList:list[str]) -> pd.DataFrame:
    # add individual game points here
    maxScores = scores.groupby(['date','gameName'])['t_score'].transform('max')
    isWinner = maxScores == scores['t_score']
    winnerCounts = isWinner.groupby([scores['date'],scores['gameName']]).transform('sum')
    scores['individual_game_point'] = ((isWinner) & (winnerCounts == 1)).astype(int)

    indivPoints = scores.groupby(['playerName','gameName'])['individual_game_point'].sum().reset_index()
    indivPointsWide = indivPoints.pivot(
        index=['playerName'],
        columns='gameName',
        values='individual_game_point'
    ).reset_index()
    indivPointsWide['individual_points'] = indivPointsWide[list(gameList)].sum(axis=1)
    return indivPointsWide

def _compute_category_points(scores: pd.DataFrame, gameList: list[str]) -> pd.DataFrame:
    # filter to only players who participated in all games
    scores['game_count'] = scores.groupby(['date','playerName'])['gameName'].transform('nunique')
    eligibleScores = scores[scores['game_count'] == len(gameList)]

    # pivot scores to wide format with date-player key and game columns
    scoresWide = eligibleScores.pivot(
        index=['date','playerName'],
        columns='gameName',
        values='t_score'
    ).reset_index()
    # ensure all game columns exist in pivot (handles games with no scores this month)
    for game in gameList:
        if game not in scoresWide.columns:
            scoresWide[game] = np.nan
    # add points column and initialize to 1. All player-date combos here have full participation and get a point
    # create new column for participation points
    scoresWide['participation_points'] = 1

    # calculate combined score
    scoresWide['total_t_score'] = scoresWide[gameList].sum(axis=1)
    maxCombined = scoresWide.groupby('date')['total_t_score'].transform('max')
    combinedWinners = scoresWide['total_t_score'] == maxCombined
    winnerCounts = combinedWinners.groupby(scoresWide['date']).transform('sum')
    uniqueCombinedWinners = combinedWinners & (winnerCounts == 1)

    # create new column for combined winner points
    scoresWide["combined_points"] = 0
    scoresWide.loc[uniqueCombinedWinners, 'combined_points'] = 1

    return scoresWide.groupby('playerName')[['participation_points','combined_points']].sum().reset_index()

def _assemble_monthly_points(widePoints: pd.DataFrame, indivPointsWide: pd.DataFrame, gamesList: list[str]) -> pd.DataFrame:
    monthlyScores = widePoints.merge(indivPointsWide, on='playerName',how='outer').fillna(0)
    monthlyScores['total_points'] = monthlyScores[['participation_points', 'combined_points', 'individual_points']].sum(axis=1)

    pointColumns = ['participation_points', 'individual_points', 'combined_points','total_points'] + list(gamesList) 
    monthlyScores = monthlyScores.melt(id_vars=['playerName'], value_vars=pointColumns,var_name='category',value_name='points')
    monthlyScores['category'] = monthlyScores['category'].str.replace('_points','', regex=False).str.capitalize()
    return monthlyScores

def calculateMonthlyPoints(games:dict, scoreEntries:list[dict[str,Any]]) -> list[PlayerMonthlyPoint]:

    scores = pd.DataFrame(scoreEntries)
    scores['t_multiplier'] = scores['gameName'].map(games)
    
    t_scores = _compute_t_scores(scores)
    indivPointsWide = _compute_individual_game_points(t_scores, list(games.keys()))
    widePoints = _compute_category_points(t_scores,list(games.keys()))
    monthlyScores = _assemble_monthly_points(widePoints, indivPointsWide, list(games.keys()))

    return[PlayerMonthlyPoint(
        playerName=score['playerName'],
        category=score['category'],
        points=score['points']
    ) for score in monthlyScores.to_dict('records')]

def calculateDailyCombinedScore(games:dict, 
                                scoreEntries: list[dict[str,Any]], 
                                date: datetime.date) -> list[ScorePublic]:
    
    scores = pd.DataFrame(scoreEntries, columns=['gameName','playerName','score'])
    gameStats = scores.groupby('gameName').agg({'score':['mean','std']}).reset_index()
    gameStats.columns = ['gameName', 'mean', 'std']

    scoresAgg = scores.merge(gameStats,on=['gameName'],how='left')
    scoresAgg['t_multiplier'] = scoresAgg['gameName'].map(games)

    scoresAgg['t_score'] = np.where(
        (scoresAgg['std'] == 0) | (scoresAgg['std'].isna()),
        0, # if only one player has played this will prevent divide by 0 errors
        (scoresAgg['score'] - scoresAgg['mean']) / scoresAgg['std'] * scoresAgg['t_multiplier']
        )
    
    # filter to only players who participated in all games
    scoresAgg['game_count'] = scoresAgg.groupby(['playerName'])['gameName'].transform('nunique')
    eligibleScores = scoresAgg[scoresAgg['game_count'] == len(games.keys())]
    
    # create combined score dataframe
    combinedScores = eligibleScores.groupby('playerName')['t_score'].sum()
    return [
        ScorePublic(
            date=date,
            playerName=str(playerName),
            gameName="Combined",
            score=int(round(t_score_sum))
        )
        for playerName, t_score_sum in combinedScores.items()
    ]
