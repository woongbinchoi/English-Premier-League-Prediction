import os
import pandas as pd
import math
from datetime import datetime
import csv

# Either year, date pair or fromFile. toFile pair needs to be fed to the function
def getRankings(year=None, date=None, fromFile=None, toFile=None):
    if not (year and date or fromFile and toFile):
        raise ValueError("Give a year/date pair or fromFile/toFile pair")
    
    if date:
        df = pd.read_csv('data/raw_cleaned/%s-%s.csv' % (year, year + 1))
        datet = datetime.strptime(date, '%Y-%m-%d')
    else:
        df = pd.read_csv(fromFile)
    scores = dict()
    for index,row in df.iterrows():
        if type(row['Date']) is float:
            continue
        if date and datetime.strptime(row['Date'], '%Y-%m-%d') > datet:
            break
        # That means this row is a prediction value
        if date and row['FTHG'] == 0 and row['FTAG'] == 0 and row['FTR'] != 'D':
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
    
    if date:
        df.to_csv('data/standings/{}Standings.csv'.format(year), index=False)
    else:
        df.to_csv(toFile, index=False)
    
    # with open('data/standings/' + str(year) + 'Standings.csv', mode='w') as standing_files:
    #   standing_writer = csv.writer(standing_files, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #   standing_writer.writerow(['Team', 'Points'])
    #   for key in sorted(scores, key=scores.get, reverse=True):
    #       standing_writer.writerow([key, scores[key]])

def getRankingsAll():
    for year in range(1993, 2019):
        print('About to get rankings on {}...'.format(year))
        getRankings(year, str(year+1) + '-12-31')
    
        
    
