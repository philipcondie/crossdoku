from sqlmodel import Session, col, select
from sqlalchemy import select as sa_select
import datetime
import pandas as pd
import numpy as np
from typing import Any

from .models import ScorePublic
from .schemas import PlayerMonthlyPoint

def calculateMonthlyPoints(games:dict, scoreEntries:list[dict[str,Any]]) -> list[PlayerMonthlyPoint]:

    scores = pd.DataFrame(scoreEntries)
    gameStats = scores.groupby(['date','gameName']).agg({'score':['mean','std']}).reset_index()
    gameStats.columns = ['date', 'gameName', 'mean', 'std']

    scores = scores.merge(gameStats,on=['date','gameName'],how='left')
    scores['t_multiplier'] = scores['gameName'].map(games)

    scores['t_score'] = np.where(
        (scores['std'] == 0) | (scores['std'].isna()),
        0, # if only one player has played this will prevent divide by 0 errors
        (scores['score'] - scores['mean']) / scores['std'] * scores['t_multiplier']
        )

    # filter to only players who participated in all games
    scores['game_count'] = scores.groupby(['date','playerName'])['gameName'].transform('nunique')
    eligibleScores = scores[scores['game_count'] == len(games.keys())]

    # pivot scores to wide format with date-player key and game columns
    scoresWide = eligibleScores.pivot(
        index=['date','playerName'],
        columns='gameName',
        values='t_score'
    ).reset_index()
    # add points column and initialize to 1. All player-date combos here have full participation and get a point
    # create new column for participation points
    scoresWide['participation_points'] = 1

    # award points for individual games
    for game in games.keys():
        maxScores = scoresWide.groupby('date')[game].transform('max')
        gameWinners = scoresWide[game] == maxScores
        winnerCounts = gameWinners.groupby(scoresWide['date']).transform('sum')
        uniqueWinners = gameWinners & (winnerCounts == 1)
        # create new column for individual game points
        scoresWide[f"{game}_points"] = 0
        scoresWide.loc[uniqueWinners,f"{game}_points"] = 1

    # calculate combined score
    scoresWide['total_t_score'] = scoresWide[games.keys()].sum(axis=1)
    maxCombined = scoresWide.groupby('date')['total_t_score'].transform('max')
    combinedWinners = scoresWide['total_t_score'] == maxCombined
    winnerCounts = combinedWinners.groupby(scoresWide['date']).transform('sum')
    uniqueCombinedWinners = combinedWinners * (winnerCounts == 1)

    # create new column for combined winner points
    scoresWide[f"combined_points"] = 0
    scoresWide.loc[uniqueCombinedWinners, 'combined_points'] += 1

    # create new column for combined ind. game points
    gameColumns = [f"{game}_points" for game in games.keys()] 
    scoresWide[f"individual_points"] = scoresWide[gameColumns].sum(axis=1)

    # create total points column and sum across other points columns
    pointColumns = ['individual_points', 'combined_points', 'participation_points']
    scoresWide['total_points'] = scoresWide[pointColumns].sum(axis=1)
    # return list of objects with player name, game name, point total attributes

    pointColumns = [col for col in scoresWide.columns if col.endswith('_points')]
    monthlyScores = scoresWide.groupby('playerName')[pointColumns].sum().reset_index()
    monthlyScores = monthlyScores.melt(id_vars=['playerName'],var_name='category',value_name='points')
    monthlyScores['category']  = monthlyScores['category'].str.replace('_points','', regex=False).str.capitalize()
    
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
