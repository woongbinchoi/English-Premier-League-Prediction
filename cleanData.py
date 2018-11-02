import ntpath
from datetime import datetime as dt
import os
import pandas as pd
import numpy as np
import math
from distutils.dir_util import copy_tree

# Copy Raw claened data to cleaned data to predict 
def copy_csv(raw_cleaned_path, cleaned_path):
    copy_tree(raw_cleaned_path, cleaned_path)

def make_directory(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

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

    # df['MatchID'] = pd.Series([str(x) for x in range(len(df))])
    # df.set_index('MatchID', inplace=True)

    df['FTHG'] = df['FTHG'].apply(convertScore)
    df['FTAG'] = df['FTAG'].apply(convertScore)
    df['Date'] = df['Date'].apply(convertDate)
    
    head, _ = ntpath.split(toPath)
    if not os.path.exists(head):
        os.makedirs(head)
    df.to_csv(toPath, index=False)


def cleanAll(fromFolder, toFolder, columns):
    for year in range(1993, 2019):
        csvFile = '%s-%s.csv' % (year, year + 1)
        frompath = ntpath.join(fromFolder, csvFile)
        topath = ntpath.join(toFolder, csvFile)
        print("Cleaning ", frompath, "...")
        clean(frompath, topath, columns)


def combineMatches(cleanedFolderPath, finalPath, startYear, endYear, makeFile=True):
    print("Combining matches from {} to {}...".format(startYear, endYear))
    dfList = []
    for year in range(startYear, endYear):
        file = '%s-%s.csv' % (year, year + 1)
        path = ntpath.join(cleanedFolderPath, file)
        df = pd.read_csv(path)
        # df.set_index('MatchID', inplace=True)
        dfList.append(df)
    df = pd.concat(dfList, ignore_index=True, sort=False)
    if makeFile:
        df.to_csv(ntpath.join(finalPath, 'final.csv'), index=False)
    return df


def getMatchResultsAgainst(filePath, cleanedFolderPath, finalPath):
    print("Getting head-to-head results...")
    teamDetail, matchDetail = {}, {}
    matchDetailColumns = [
        'HT_win_rate_against',
        'AT_win_rate_against'
    ]

    for item in matchDetailColumns:
        matchDetail[item] = []

    df = combineMatches(cleanedFolderPath, finalPath, 1993, 2019, makeFile=False)
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


