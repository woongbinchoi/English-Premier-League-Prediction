import os
import pandas as pd
import requests
import numpy as np
from datetime import datetime

# Deprecated function. Use getRankings from rankings.py
def getScore(team1, team2, date, fromYear=2006, toYear=2019):
    datet = datetime.strptime(date, '%d/%m/%y')
    score = [0, 0, 0]
    for year in range(fromYear, toYear):
        path = 'data/cleaned/%s-%s.csv' % (year, year + 1)
        df = pd.read_csv(path)
        for index,row in df.iterrows():
            if datet < datetime.strptime(row['Date'], '%d/%m/%y'):
                return score
            if team1 == row['HomeTeam'] and team2 == row['AwayTeam']:
                if row['FTR'] == 'H':
                    score[0] += 1
                elif row['FTR'] == 'A':
                    score[1] += 1
                else:
                    score[2] += 1
            elif team1 == row['AwayTeam'] and team2 == row['HomeTeam']:
                if row['FTR'] == 'A':
                    score[0] += 1
                elif row['FTR'] == 'H':
                    score[1] += 1
                else:
                    score[2] += 1
    return score

# Deprecated function. Use getRankings from rankings.py
def getAllTime(fromYear=2006, toYear=2019):
    scores = dict()
    for year in range(fromYear, toYear):
        path = 'data/cleaned/%s-%s.csv' % (year, year + 1)
        df = pd.read_csv(path)
        for index,row in df.iterrows():
            away = row['AwayTeam']
            home = row['HomeTeam']
            if type(away) is float:
                break
            swapped = False
            if away < home:
                key = away + "-" + home
            else:
                key = home + "-" + away
                swapped = True
            if key not in scores:
                scores[key] = [0, 0, 0];
            score = scores[key]
            if row['FTR'] == 'D':
                score[2] += 1
            elif (row['FTR'] == 'A' and not swapped) or (row['FTR'] == 'H' and swapped):
                score[0] += 1
            else:
                score[1] += 1
    for key in scores:
        print (key)
        print (scores[key])
    return scores


def convertTeamName(team):
    teamMap = {
        'Manchester United FC': 'Man United',
        'Leicester City FC': 'Leicester',
        'Tottenham Hotspur FC': 'Tottenham',
        'Newcastle United FC': 'Newcastle',
        'Chelsea FC': 'Chelsea',
        'Huddersfield Town AFC': 'Huddersfield',
        'Crystal Palace FC': 'Crystal Palace',
        'Fulham FC': 'Fulham',
        'AFC Bournemouth': 'Bournemouth',
        'Cardiff City FC': 'Cardiff',
        'Watford FC': 'Watford',
        'Brighton & Hove Albion FC': 'Brighton',
        'Wolverhampton Wanderers FC': 'Wolves',
        'Everton FC': 'Everton',
        'Arsenal FC': 'Arsenal',
        'Manchester City FC': 'Man City',
        'Liverpool FC': 'Liverpool',
        'West Ham United FC': 'West Ham',
        'Southampton FC': 'Southampton',
        'Burnley FC': 'Burnley'
    }

    return teamMap[team]

def getCurrentFixtures(rawDataCurrentPath):
    base_url = "http://api.football-data.org/v2/competitions/"
    AUTH_TOKEN = "9f2efd00a5604f59a8f1c54860786e31"
    headers={"X-Auth-Token": AUTH_TOKEN}
    
    print("Getting results and fixtures for this year...")
    
    england_area_code = 2072
    list_competitions_url = base_url + "?areas=" + str(england_area_code)
    req = requests.get(list_competitions_url, headers=headers).json()
    premier_league_data = [x for x in req['competitions'] if x['name'] == 'Premier League'][0]
    premier_league_id = premier_league_data['id']

    matches_url = base_url + str(premier_league_id) + "/matches"
    match_data = requests.get(matches_url, headers=headers).json()['matches']
    
    matches_dict = {
        'Date': [match['utcDate'].split('T')[0] for match in match_data],
        'HomeTeam': [convertTeamName(match['homeTeam']['name']) for match in match_data],
        'AwayTeam': [convertTeamName(match['awayTeam']['name']) for match in match_data],
        'FTHG': [match['score']['fullTime']['homeTeam'] if match['status'] == "FINISHED" else np.nan for match in match_data],
        'FTAG': [match['score']['fullTime']['awayTeam'] if match['status'] == "FINISHED" else np.nan for match in match_data],
        'FTR': [match['score']['winner'][0] if match['status'] == "FINISHED" and match['score']['winner'] else "" for match in match_data]
    }

    df = pd.DataFrame(matches_dict)
    df.to_csv(rawDataCurrentPath, index=False)
    
