import pandas as pd
import numpy as np
import os
import datetime

# Helpers
# Identify Win/Loss Streaks if any.
def get_3game_ws(last_matches):
    if hasattr(last_matches, "__len__"):
        return 1 if len(last_matches) > 3 and last_matches[-3:] == 'WWW' else 0
    return np.nan
    
def get_5game_ws(last_matches):
    if hasattr(last_matches, "__len__"):
        return 1 if last_matches == 'WWWWW' else 0
    return np.nan
    
def get_3game_ls(last_matches):
    if hasattr(last_matches, "__len__"):
        return 1 if len(last_matches) > 3 and last_matches[-3:] == 'LLL' else 0
    return np.nan
    
def get_5game_ls(last_matches):
    if hasattr(last_matches, "__len__"):
        return 1 if last_matches == 'LLLLL' else 0
    return np.nan

def get_5win_rate(last_matches):
    if hasattr(last_matches, "__len__") and len(last_matches) == 5:
        win_count = last_matches.count('W')
        return win_count / len(last_matches)
    else:
        return np.nan



def getCurrentSeason():
    now = datetime.datetime.now()
    # By July, fixture of the season should be available.
    new_season_start = datetime.datetime(now.year, 7, 1)
    return now.year if now > new_season_start else now.year - 1

# Calculate match played, current standing, goal for, goal against, goal difference, winning/losing streaks, etc.
# Input is csv that is just cleaned from raw data
# Output is csv modified with each row added match played, current standing, GF, GA, GD, winning/losing streaks, etc.
def addCurrentDetails(frompath, topath, standings_path, yearAvailableFrom):
    teamDetail, matchDetail = {}, {}
    matchDetailColumns = [
        'HT_match_played',
        'HT_current_standing',
        'HT_past_standing',
        'HT_past_goal_diff',
        'HT_past_win_rate',
        'HT_goal_for',
        'HT_goal_against',
        'HT_goal_diff',
        'HT_win_rate_season',
        'AT_match_played',
        'AT_current_standing',
        'AT_past_standing',
        'AT_past_goal_diff',
        'AT_past_win_rate',
        'AT_goal_for',
        'AT_goal_against',
        'AT_goal_diff',
        'AT_win_rate_season',
        'HT_last_5',
        'HT_last_4',
        'HT_last_3',
        'HT_last_2',
        'HT_last_1',
        'AT_last_5',
        'AT_last_4',
        'AT_last_3',
        'AT_last_2',
        'AT_last_1'
    ]

    for item in matchDetailColumns:
        matchDetail[item] = []

    df = pd.read_csv(frompath)

    previousYear = int(frompath[-13:-9]) - 1
    standings = dict()
    # We only have data from 1993 to current. That means We don't have 'previous year' data at 1993.
    if previousYear > yearAvailableFrom:
        dfstandings = pd.read_csv('{}/{}-{}.csv'.format(standings_path, previousYear, previousYear + 1))
        for index,row in dfstandings.iterrows():
            standings[row['Team']] = dict()
            standings[row['Team']]['Points'] = row['Points']
            standings[row['Team']]['Goal_Diff'] = row['Goal_Diff']
            standings[row['Team']]['Win_Rate'] = row['Win_Rate']

    for index, row in df.iterrows():
        HT = row['HomeTeam']
        AT = row['AwayTeam']

        if HT not in teamDetail:
            teamDetail[HT] = {
                'match_played': 0,
                'win': 0,
                'current_standing': 0,
                'past_standing': standings[HT]['Points'] if HT in standings else -1,
                'past_goal_diff': standings[HT]['Goal_Diff'] if HT in standings else -1,
                'past_win_rate': standings[HT]['Win_Rate'] if HT in standings else 0,
                'goal_for': 0,
                'goal_against': 0,
                'goal_difference': 0,
                'last_5_matches': [""] * 5
            }
        if AT not in teamDetail:
            teamDetail[AT] = {
                'match_played': 0,
                'win': 0,
                'current_standing': 0,
                'past_standing': standings[AT]['Points'] if AT in standings else -1,
                'past_goal_diff': standings[AT]['Goal_Diff'] if AT in standings else -1,
                'past_win_rate': standings[AT]['Win_Rate'] if AT in standings else 0,
                'goal_for': 0,
                'goal_against': 0,
                'goal_difference': 0,
                'last_5_matches': [""] * 5
            }

        TD_HT = teamDetail[HT]
        TD_AT = teamDetail[AT]
        
        if len(TD_HT['last_5_matches']) != 5 or len(TD_AT['last_5_matches']) != 5:
            break

        matchDetail['HT_match_played'].append(TD_HT['match_played'])
        matchDetail['HT_current_standing'].append(TD_HT['current_standing'])
        matchDetail['HT_past_standing'].append(TD_HT['past_standing'])
        matchDetail['HT_past_goal_diff'].append(TD_HT['past_goal_diff'])
        matchDetail['HT_past_win_rate'].append(TD_HT['past_win_rate'])
        matchDetail['HT_goal_for'].append(TD_HT['goal_for'])
        matchDetail['HT_goal_against'].append(TD_HT['goal_against'])
        matchDetail['HT_goal_diff'].append(TD_HT['goal_difference'])
        matchDetail['AT_match_played'].append(TD_AT['match_played'])
        matchDetail['AT_current_standing'].append(TD_AT['current_standing'])
        matchDetail['AT_past_standing'].append(TD_AT['past_standing'])
        matchDetail['AT_past_goal_diff'].append(TD_AT['past_goal_diff'])
        matchDetail['AT_past_win_rate'].append(TD_AT['past_win_rate'])
        matchDetail['AT_goal_for'].append(TD_AT['goal_for'])
        matchDetail['AT_goal_against'].append(TD_AT['goal_against'])
        matchDetail['AT_goal_diff'].append(TD_AT['goal_difference'])
        matchDetail['HT_win_rate_season'].append(TD_HT['win'] / TD_HT['match_played'] if TD_HT['match_played'] > 0 else np.nan)
        matchDetail['AT_win_rate_season'].append(TD_AT['win'] / TD_AT['match_played'] if TD_AT['match_played'] > 0 else np.nan)

        matchDetail['HT_last_5'].append(TD_HT['last_5_matches'][0])
        matchDetail['AT_last_5'].append(TD_AT['last_5_matches'][0])
        matchDetail['HT_last_4'].append(TD_HT['last_5_matches'][1])        
        matchDetail['AT_last_4'].append(TD_AT['last_5_matches'][1])
        matchDetail['HT_last_3'].append(TD_HT['last_5_matches'][2])
        matchDetail['AT_last_3'].append(TD_AT['last_5_matches'][2])
        matchDetail['HT_last_2'].append(TD_HT['last_5_matches'][3])
        matchDetail['AT_last_2'].append(TD_AT['last_5_matches'][3])
        matchDetail['HT_last_1'].append(TD_HT['last_5_matches'][4])
        matchDetail['AT_last_1'].append(TD_AT['last_5_matches'][4])


        TD_HT['match_played'] += 1
        TD_AT['match_played'] += 1
        TD_HT['goal_for'] += row['FTHG']
        TD_AT['goal_for'] += row['FTAG']
        TD_HT['goal_against'] += row['FTAG']
        TD_AT['goal_against'] += row['FTHG']

        gd = row['FTHG'] - row['FTAG']
        TD_HT['goal_difference'] += gd
        TD_AT['goal_difference'] -= gd

        TD_HT['last_5_matches'].pop(0)
        TD_AT['last_5_matches'].pop(0)

        gameResult = row['FTR']
        if gameResult == 'H':
            TD_HT['current_standing'] += 3
            TD_HT['win'] += 1
            TD_HT['last_5_matches'].append('W')
            TD_AT['last_5_matches'].append('L')
        elif gameResult == 'A':
            TD_AT['current_standing'] += 3
            TD_AT['win'] += 1
            TD_HT['last_5_matches'].append('L')
            TD_AT['last_5_matches'].append('W')
        elif gameResult == 'D': 
            TD_HT['current_standing'] += 1
            TD_AT['current_standing'] += 1
            TD_HT['last_5_matches'].append('D')
            TD_AT['last_5_matches'].append('D')

    columnList = list(df)

    for key, matchResults in matchDetail.items():
        df[key] = pd.Series(matchResults)
    df = df[columnList + matchDetailColumns]

    df['HT_last_matches'] = df['HT_last_5'] + df['HT_last_4'] + df['HT_last_3'] + df['HT_last_2'] + df['HT_last_1']
    df['AT_last_matches'] = df['AT_last_5'] + df['AT_last_4'] + df['AT_last_3'] + df['AT_last_2'] + df['AT_last_1']
    df['HT_3_win_streak'] = df['HT_last_matches'].apply(get_3game_ws)
    df['HT_5_win_streak'] = df['HT_last_matches'].apply(get_5game_ws)
    df['HT_3_lose_Streak'] = df['HT_last_matches'].apply(get_3game_ls)
    df['HT_5_lose_Streak'] = df['HT_last_matches'].apply(get_5game_ls)
    df['AT_3_win_streak'] = df['AT_last_matches'].apply(get_3game_ws)
    df['AT_5_win_streak'] = df['AT_last_matches'].apply(get_5game_ws)
    df['AT_3_lose_Streak'] = df['AT_last_matches'].apply(get_3game_ls)
    df['AT_5_lose_Streak'] = df['AT_last_matches'].apply(get_5game_ls)
    df['HT_5_win_rate'] = df['HT_last_matches'].apply(get_5win_rate)
    df['AT_5_win_rate'] = df['AT_last_matches'].apply(get_5win_rate)
    df['current_standing_diff'] = df['HT_current_standing'] - df['AT_current_standing']
    df['past_standing_diff'] = df['HT_past_standing'] - df['AT_past_standing']
    df['past_goal_diff_diff'] = df['HT_past_goal_diff'] - df['AT_past_goal_diff']
    df['past_win_rate_diff'] = df['HT_past_win_rate'] - df['AT_past_win_rate']
    df['past_standing_diff'] = df['HT_past_standing'] - df['AT_past_standing']
    df['win_rate_season_diff'] = df['HT_win_rate_season'] - df['AT_win_rate_season']
    df['goal_diff_diff'] = df['HT_goal_diff'] - df['AT_goal_diff']

    dropLabels = ['HT_last_' + str(x+1) for x in range(5)] + ['AT_last_' + str(x+1) for x in range(5)]
    dropLabels += ['HT_last_matches', 'AT_last_matches']
    df = df.drop(columns=dropLabels)

    df.to_csv(topath, index=False)

def addCurrentDetailsAll(fromFolderPath, toFolderPath, standings_path, fromYear, toYear, yearAvailableFrom):
    for year in range(fromYear, toYear + 1):
        file = '{}-{}.csv'.format(year, year + 1)
        frompath = os.path.join(fromFolderPath, file)
        topath = os.path.join(toFolderPath, file)
        print("About to add 'current details' from {} to {}...".format(frompath, topath))
        addCurrentDetails(frompath, topath, standings_path, yearAvailableFrom)
    