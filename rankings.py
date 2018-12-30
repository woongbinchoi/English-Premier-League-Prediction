import os
import pandas as pd
import numpy as np
import math
from datetime import datetime
import csv
from cleanData import make_directory

# If date is specified, calculate ranking up until that date
def getRankings(fromFile, toFile, date=None, include_prediction=False, predicted_date_so_far=None, ranking_summary_file=None):
    if date:
        datet = datetime.strptime(date, '%Y-%m-%d')
    if not (fromFile and toFile):
        raise ValueError("Error: getRankings: Give a fromFile/toFile pair")
    
    df = pd.read_csv(fromFile)

    scores = dict()
    for index,row in df.iterrows():
        if type(row['Date']) is float:
            continue
        if date and datetime.strptime(row['Date'], '%Y-%m-%d') > datet:
            break
        # That means this row is a prediction value
        if not include_prediction and row['FTHG'] == 0 and row['FTAG'] == 0 and row['FTR'] != 'D':
            break
        # Meaning this game is not played and not predicted yet
        if row['FTR'] is np.nan:
            break
        home = row['HomeTeam']
        away = row['AwayTeam']
        if home not in scores:
            scores[home] = {
                'match_played': 0,
                'points': 0,
                'goal_diff': 0,
                'win': 0
            }
        if away not in scores:
            scores[away] = {
                'match_played': 0,
                'points': 0,
                'goal_diff': 0,
                'win': 0
            }

        scores[home]['match_played'] += 1
        scores[away]['match_played'] += 1
        match_goal_diff = row['FTHG'] - row['FTAG']
        scores[home]['goal_diff'] += match_goal_diff
        scores[away]['goal_diff'] -= match_goal_diff
        if row['FTR'] == 'H':
            scores[home]['points'] += 3
            scores[home]['win'] += 1
        elif row['FTR'] == 'A':
            scores[away]['points'] += 3
            scores[away]['win'] += 1
        else:
            scores[home]['points'] += 1
            scores[away]['points'] += 1

    Team = sorted(scores, key=lambda k: scores[k]['points'], reverse=True)
    Points, Goal_Diff, Win_Rate = [], [], []
    for name in Team:
        val = scores[name]
        Points.append(val['points'])
        Goal_Diff.append(val['goal_diff'])
        Win_Rate.append(val['win'] / val['match_played'])
    df = pd.DataFrame(list(zip(Team, Points, Goal_Diff, Win_Rate)), columns=['Team', 'Points', 'Goal_Diff', 'Win_Rate'])
    
    make_directory(toFile)
    df.to_csv(toFile, index=False)
    
    if include_prediction and predicted_date_so_far and ranking_summary_file:
        round_df = pd.DataFrame(list(zip(Team, Points)), columns=['Team', predicted_date_so_far])
        round_df.set_index('Team', inplace=True)
        round_df = round_df.transpose()
        round_df.index.name = 'Date'
        
        if os.path.isfile(ranking_summary_file):
            summary_df = pd.read_csv(ranking_summary_file)
            summary_df.set_index('Date', inplace=True)
            summary_df = pd.concat([summary_df, round_df], sort=False)
            summary_df.to_csv(ranking_summary_file)
        else:
            round_df.to_csv(ranking_summary_file)


def getRankingsAll(fromYear, toYear, fromFileFolderPath, toFileFolderPath):
    for year in range(fromYear, toYear + 1):
        print('About to get rankings on {}...'.format(year))
        csv_file = '{}-{}.csv'.format(year, year + 1)
        fromFile = os.path.join(fromFileFolderPath, csv_file)
        toFile = os.path.join(toFileFolderPath, csv_file)
        getRankings(fromFile, toFile, '{}-12-31'.format(str(year+1)), include_prediction=False)

    
        
    