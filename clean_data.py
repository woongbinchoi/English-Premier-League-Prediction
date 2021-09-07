import ntpath
from datetime import datetime as dt
import os
import pandas as pd
import numpy as np
import math
import sqlite3


# clean the original raw data by storing only the columns that we need, and removing the rest.
def clean(from_path, to_path, columns):
    def convert_date(date):
        if date == '':
            return None
        else:
            if len(date.split('-')) == 3:
                return date

            year = date.split('/')[-1]
            if len(year) == 4:
                return dt.strptime(date, '%d/%m/%Y').date()
            else:
                return dt.strptime(date, '%d/%m/%y').date()
    def convert_score(score):
        if math.isnan(score):
            return score
        else:
            return int(score)

    df = pd.read_csv(from_path, error_bad_lines=False)
    df = df[columns]
    df = df[pd.notnull(df['Date'])]

    df['FTHG'] = df['FTHG'].apply(convert_score)
    df['FTAG'] = df['FTAG'].apply(convert_score)
    df['Date'] = df['Date'].apply(convert_date)
    
    head, _ = ntpath.split(to_path)
    if not os.path.exists(head):
        os.makedirs(head)
    df.to_csv(to_path, index=False)


def clean_all(from_folder, to_folder, from_year, to_year):
    columns = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    for year in range(from_year, to_year + 1):
        csvFile = '{}-{}.csv'.format(year, year + 1)
        from_path = os.path.join(from_folder, csvFile)
        to_path = os.path.join(to_folder, csvFile)
        print("Cleaning ", from_path, "...")
        clean(from_path, to_path, columns)


def combine_matches(cleaned_folder_path, final_path, start_year, end_year, make_file=True):
    print("Combining matches from {} to {}...".format(start_year, end_year))
    dfList = []
    for year in range(start_year, end_year + 1):
        file = '{}-{}.csv'.format(year, year + 1)
        path = os.path.join(cleaned_folder_path, file)
        df = pd.read_csv(path)
        dfList.append(df)
    df = pd.concat(dfList, ignore_index=True, sort=False)
    if make_file:
        df.to_csv(final_path, index=False)
    return df


def get_match_results_against(file_path, cleaned_folder_path, final_path, from_year, to_year):
    print("Getting head-to-head results...")
    team_detail, match_detail = {}, {}
    match_detail_columns = [
        'HT_win_rate_against',
        'AT_win_rate_against'
    ]

    for item in match_detail_columns:
        match_detail[item] = []

    # Get head-to-head result from from_year to to_year
    df = combine_matches(cleaned_folder_path, final_path, from_year, to_year, make_file=False)
    for _, row in df.iterrows():
        HT = row['HomeTeam']
        AT = row['AwayTeam']

        if HT not in team_detail:
            team_detail[HT] = {}
        if AT not in team_detail:
            team_detail[AT] = {}
        if AT not in team_detail[HT]:
            team_detail[HT][AT] = {
                'match_played': 0,
                'win': 0
            }
        if HT not in team_detail[AT]:
            team_detail[AT][HT] = {
                'match_played': 0,
                'win': 0
            }

        TD_HT_AT = team_detail[HT][AT]
        TD_AT_HT = team_detail[AT][HT]
        HT_WR = TD_HT_AT['win'] / TD_HT_AT['match_played'] if TD_HT_AT['match_played'] > 0 else np.nan
        AT_WR = TD_AT_HT['win'] / TD_AT_HT['match_played'] if TD_AT_HT['match_played'] > 0 else np.nan
        match_detail['HT_win_rate_against'].append(HT_WR)
        match_detail['AT_win_rate_against'].append(AT_WR)

        TD_HT_AT['match_played'] += 1
        TD_AT_HT['match_played'] += 1

        game_result = row['FTR']
        if game_result == 'H':
            TD_HT_AT['win'] += 1
        elif game_result == 'A':
            TD_AT_HT['win'] += 1
            
    # Only take the last x results of df and combine with filedf. This is because we don't always want to merge all data from 1993 to 2018
    filedf = pd.read_csv(file_path)
    row_count = filedf.shape[0]
    filedf['HT_win_rate_against'] = pd.Series(match_detail['HT_win_rate_against'][-row_count:], index=filedf.index)
    filedf['AT_win_rate_against'] = pd.Series(match_detail['AT_win_rate_against'][-row_count:], index=filedf.index)
    filedf.to_csv(file_path, index=False)


def remove_goal_scores(final_path):
    print("Removing Goal Scores...")
    df = pd.read_csv(final_path)
    df = df.drop(columns=['FTHG','FTAG'])
    df.to_csv(final_path, index=False)


def save_new_data_to_database(database_path, final_data_file, prediction_results_file, standing_predictions_file,
                          final_data_file_name='previous_results', prediction_results_file_name='prediction_results',
                          standing_predictions_file_name='prediction_rankings'):
    conn = sqlite3.connect(database_path)
    
    previous_results_df = pd.read_csv(final_data_file)
    previous_results_df = previous_results_df[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]]
    previous_results_df = previous_results_df.loc[(previous_results_df['FTHG'] != 0) | 
                            (previous_results_df['FTAG'] != 0) | 
                            ((previous_results_df['FTR'] != 'A') & 
                                (previous_results_df['FTR'] != 'H'))]
    
    prediction_results_df = pd.read_csv(prediction_results_file)
    prediction_results_df = prediction_results_df[["Date", "HomeTeam", "AwayTeam", "FTR", "prob_A", "prob_D", "prob_H"]]
    prediction_results_df = prediction_results_df.loc[prediction_results_df['prob_A'].notna()]
    
    standing_result_df = pd.read_csv(standing_predictions_file)
    
    previous_results_df.to_sql(final_data_file_name, con=conn, if_exists='replace')
    prediction_results_df.to_sql(prediction_results_file_name, con=conn, if_exists='replace')
    standing_result_df.to_sql(standing_predictions_file_name, con=conn, if_exists='replace')


def save_summary_to_database(database_path, best_clf_average, winner):
    conn = sqlite3.connect(database_path)
    cur = conn.cursor()
    
    cur.execute('DROP TABLE IF EXISTS summary')
    cur.execute('CREATE TABLE summary (time DATE, accuracy NUMBER, winner TEXT)')
    cur.execute('INSERT INTO summary (time, accuracy, winner) VALUES (?, ?, ?)', 
                (dt.now().strftime('%Y-%m-%d'), best_clf_average, winner))
    conn.commit()
