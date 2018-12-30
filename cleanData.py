import ntpath
from datetime import datetime as dt
import os
import pandas as pd
import numpy as np
import math
from distutils.dir_util import copy_tree
from shutil import rmtree
import sqlite3

# Use this function to copy a file or a folder
def copy_csv(fromPath, toPath):
    make_directory(toPath)
    if os.path.isfile(fromPath):
        with open(toPath, 'w') as toFile, open(fromPath, 'r') as fromFile:
            for line in fromFile:
                    toFile.write(line)
    elif os.path.isdir(fromPath):
        copy_tree(fromPath, toPath)
    else:
        raise ValueError("Copy_CSV Error. File either does not exist, or is an unsupported file type")

def make_directory(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def remove_directory(path):
    if os.path.exists(path):
        rmtree(path)

# clean the original raw data by storing only the columns that we need, and removing the rest.
def clean(fromPath, toPath, columns):
    def convertDate(date):
        if date == '':
            return None
        else:
            _, file = ntpath.split(toPath)
            if len(date.split('-')) == 3:
                return date
            elif file == '2002-2003.csv':
                # Only this file has a different date format
                return dt.strptime(date, '%d/%m/%Y').date()
            else:
                return dt.strptime(date, '%d/%m/%y').date()
    def convertScore(score):
        if math.isnan(score):
            return score
        else:
            return int(score)

    df = pd.read_csv(fromPath, error_bad_lines=False)
    df = df[columns]
    df = df[pd.notnull(df['Date'])]

    df['FTHG'] = df['FTHG'].apply(convertScore)
    df['FTAG'] = df['FTAG'].apply(convertScore)
    df['Date'] = df['Date'].apply(convertDate)
    
    head, _ = ntpath.split(toPath)
    if not os.path.exists(head):
        os.makedirs(head)
    df.to_csv(toPath, index=False)


def cleanAll(fromFolder, toFolder, columns, fromYear, toYear):
    for year in range(fromYear, toYear + 1):
        csvFile = '{}-{}.csv'.format(year, year + 1)
        frompath = os.path.join(fromFolder, csvFile)
        topath = os.path.join(toFolder, csvFile)
        print("Cleaning ", frompath, "...")
        clean(frompath, topath, columns)


def combineMatches(cleanedFolderPath, finalPath, startYear, endYear, makeFile=True):
    print("Combining matches from {} to {}...".format(startYear, endYear))
    dfList = []
    for year in range(startYear, endYear + 1):
        file = '{}-{}.csv'.format(year, year + 1)
        path = os.path.join(cleanedFolderPath, file)
        df = pd.read_csv(path)
        dfList.append(df)
    df = pd.concat(dfList, ignore_index=True, sort=False)
    if makeFile:
        df.to_csv(finalPath, index=False)
    return df


def getMatchResultsAgainst(filePath, cleanedFolderPath, finalPath, fromYear, toYear):
    print("Getting head-to-head results...")
    teamDetail, matchDetail = {}, {}
    matchDetailColumns = [
        'HT_win_rate_against',
        'AT_win_rate_against'
    ]

    for item in matchDetailColumns:
        matchDetail[item] = []

    # Get head-to-head result from fromYear to toYear
    df = combineMatches(cleanedFolderPath, finalPath, fromYear, toYear, makeFile=False)
    for index, row in df.iterrows():
        HT = row['HomeTeam']
        AT = row['AwayTeam']

        if HT not in teamDetail:
            teamDetail[HT] = {}
        if AT not in teamDetail:
            teamDetail[AT] = {}
        if AT not in teamDetail[HT]:
            teamDetail[HT][AT] = {
                'match_played': 0,
                'win': 0
            }
        if HT not in teamDetail[AT]:
            teamDetail[AT][HT] = {
                'match_played': 0,
                'win': 0
            }

        TD_HT_AT = teamDetail[HT][AT]
        TD_AT_HT = teamDetail[AT][HT]
        HT_WR = TD_HT_AT['win'] / TD_HT_AT['match_played'] if TD_HT_AT['match_played'] > 0 else np.nan
        AT_WR = TD_AT_HT['win'] / TD_AT_HT['match_played'] if TD_AT_HT['match_played'] > 0 else np.nan
        matchDetail['HT_win_rate_against'].append(HT_WR)
        matchDetail['AT_win_rate_against'].append(AT_WR)

        TD_HT_AT['match_played'] += 1
        TD_AT_HT['match_played'] += 1

        gameResult = row['FTR']
        if gameResult == 'H':
            TD_HT_AT['win'] += 1
        elif gameResult == 'A':
            TD_AT_HT['win'] += 1
            
    # Only take the last x results of df and combine with filedf. This is because we don't always want to merge all data from 1993 to 2018
    filedf = pd.read_csv(filePath)
    row_count = filedf.shape[0]
    filedf['HT_win_rate_against'] = pd.Series(matchDetail['HT_win_rate_against'][-row_count:], index=filedf.index)
    filedf['AT_win_rate_against'] = pd.Series(matchDetail['AT_win_rate_against'][-row_count:], index=filedf.index)
    filedf.to_csv(filePath, index=False)


def removeGoalScores(finalPath):
    print("Removing Goal Scores...")
    df = pd.read_csv(finalPath)
    df = df.drop(columns=['FTHG','FTAG'])
    df.to_csv(finalPath, index=False)


def saveNewDataToDatabase(database_path, final_data_file, prediction_results_file, standing_predictions_file,
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
    

