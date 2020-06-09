import os
import pandas as pd
import numpy as np
import math
from datetime import datetime
import csv
from helpers import make_directory

# If date is specified, calculate ranking up until that date
def get_rankings(from_file, to_file, date=None, include_prediction=False, predicted_date_so_far=None, ranking_summary_file=None):
    if date:
        datet = datetime.strptime(date, '%Y-%m-%d')
    if not (from_file and to_file):
        raise ValueError("Error: get_rankings: Give a from_file/to_file pair")
    
    df = pd.read_csv(from_file)

    scores = dict()
    for _, row in df.iterrows():
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

    teams = sorted(scores, key=lambda k: scores[k]['points'], reverse=True)
    points, goal_diff, win_rate = [], [], []
    for name in teams:
        val = scores[name]
        points.append(val['points'])
        goal_diff.append(val['goal_diff'])
        win_rate.append(val['win'] / val['match_played'])
    df = pd.DataFrame(list(zip(teams, points, goal_diff, win_rate)), columns=['Team', 'Points', 'Goal_Diff', 'Win_Rate'])
    
    make_directory(to_file)
    df.to_csv(to_file, index=False)
    
    if include_prediction and predicted_date_so_far and ranking_summary_file:
        round_df = pd.DataFrame(list(zip(teams, points)), columns=['Team', predicted_date_so_far])
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

    return teams[0]


def get_rankings_all(from_year, to_year, from_file_folder_path, to_file_folder_path):
    for year in range(from_year, to_year + 1):
        print('About to get rankings on {}...'.format(year))
        csv_file = '{}-{}.csv'.format(year, year + 1)
        from_file = os.path.join(from_file_folder_path, csv_file)
        to_file = os.path.join(to_file_folder_path, csv_file)
        get_rankings(from_file, to_file, '{}-12-31'.format(str(year+1)), include_prediction=False)
