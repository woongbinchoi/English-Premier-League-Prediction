import pandas as pd
import numpy as np
import os
import datetime


# Calculate match played, current standing, goal for, goal against, goal difference, winning/losing streaks, etc.
# Input is csv that is just cleaned from raw data
# Output is csv modified with each row added match played, current standing, GF, GA, GD, winning/losing streaks, etc.
def add_current_details(from_path, to_path, standings_path, year_available_from):
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

    team_detail, match_detail = {}, {}
    match_detail_columns = [
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

    for item in match_detail_columns:
        match_detail[item] = []

    df = pd.read_csv(from_path)

    previous_year = int(from_path[-13:-9]) - 1
    standings = dict()
    # We only have data from 1993 to current. That means We don't have 'previous year' data at 1993.
    if previous_year > year_available_from:
        dfstandings = pd.read_csv('{}/{}-{}.csv'.format(standings_path, previous_year, previous_year + 1))
        for _,row in dfstandings.iterrows():
            standings[row['Team']] = dict()
            standings[row['Team']]['Points'] = row['Points']
            standings[row['Team']]['Goal_Diff'] = row['Goal_Diff']
            standings[row['Team']]['Win_Rate'] = row['Win_Rate']

    for _, row in df.iterrows():
        HT = row['HomeTeam']
        AT = row['AwayTeam']

        if HT not in team_detail:
            team_detail[HT] = {
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
        if AT not in team_detail:
            team_detail[AT] = {
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

        TD_HT = team_detail[HT]
        TD_AT = team_detail[AT]
        
        if len(TD_HT['last_5_matches']) != 5 or len(TD_AT['last_5_matches']) != 5:
            break

        match_detail['HT_match_played'].append(TD_HT['match_played'])
        match_detail['HT_current_standing'].append(TD_HT['current_standing'])
        match_detail['HT_past_standing'].append(TD_HT['past_standing'])
        match_detail['HT_past_goal_diff'].append(TD_HT['past_goal_diff'])
        match_detail['HT_past_win_rate'].append(TD_HT['past_win_rate'])
        match_detail['HT_goal_for'].append(TD_HT['goal_for'])
        match_detail['HT_goal_against'].append(TD_HT['goal_against'])
        match_detail['HT_goal_diff'].append(TD_HT['goal_difference'])
        match_detail['AT_match_played'].append(TD_AT['match_played'])
        match_detail['AT_current_standing'].append(TD_AT['current_standing'])
        match_detail['AT_past_standing'].append(TD_AT['past_standing'])
        match_detail['AT_past_goal_diff'].append(TD_AT['past_goal_diff'])
        match_detail['AT_past_win_rate'].append(TD_AT['past_win_rate'])
        match_detail['AT_goal_for'].append(TD_AT['goal_for'])
        match_detail['AT_goal_against'].append(TD_AT['goal_against'])
        match_detail['AT_goal_diff'].append(TD_AT['goal_difference'])
        match_detail['HT_win_rate_season'].append(TD_HT['win'] / TD_HT['match_played'] if TD_HT['match_played'] > 0 else np.nan)
        match_detail['AT_win_rate_season'].append(TD_AT['win'] / TD_AT['match_played'] if TD_AT['match_played'] > 0 else np.nan)

        match_detail['HT_last_5'].append(TD_HT['last_5_matches'][0])
        match_detail['AT_last_5'].append(TD_AT['last_5_matches'][0])
        match_detail['HT_last_4'].append(TD_HT['last_5_matches'][1])        
        match_detail['AT_last_4'].append(TD_AT['last_5_matches'][1])
        match_detail['HT_last_3'].append(TD_HT['last_5_matches'][2])
        match_detail['AT_last_3'].append(TD_AT['last_5_matches'][2])
        match_detail['HT_last_2'].append(TD_HT['last_5_matches'][3])
        match_detail['AT_last_2'].append(TD_AT['last_5_matches'][3])
        match_detail['HT_last_1'].append(TD_HT['last_5_matches'][4])
        match_detail['AT_last_1'].append(TD_AT['last_5_matches'][4])

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

    column_list = list(df)

    for key, matchResults in match_detail.items():
        df[key] = pd.Series(matchResults)
    df = df[column_list + match_detail_columns]

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

    drop_labels = ['HT_last_' + str(x+1) for x in range(5)] + ['AT_last_' + str(x+1) for x in range(5)]
    drop_labels += ['HT_last_matches', 'AT_last_matches']
    df = df.drop(columns=drop_labels)
    df.to_csv(to_path, index=False)


def add_current_details_all(from_folder_path, to_folder_path, standings_path, from_year, to_year, year_available_from):
    for year in range(from_year, to_year + 1):
        file = '{}-{}.csv'.format(year, year + 1)
        from_path = os.path.join(from_folder_path, file)
        to_path = os.path.join(to_folder_path, file)
        print("About to add 'current details' from {} to {}...".format(from_path, to_path))
        add_current_details(from_path, to_path, standings_path, year_available_from)
