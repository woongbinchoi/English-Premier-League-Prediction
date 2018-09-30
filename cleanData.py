import ntpath
from datetime import datetime as dt
import os
import pandas as pd
import numpy as np
from sofifaScraper import mergeOVAToCleanedAll
from currentStatus import addCurrentDetailsAll


# clean the original raw data by storing only the columns that we need, and removing the rest.
def clean(fromPath, toPath, columns):
    def convertDate(date):
        if date == '':
            return None
        else:
            _, file = ntpath.split(toPath)
            if file == '2002-2003.csv':
                return dt.strptime(date, '%d/%m/%Y').date()
            else:
                return dt.strptime(date, '%d/%m/%y').date()

    df = pd.read_csv(fromPath, error_bad_lines=False)
    df = df[columns]
    df = df[pd.notnull(df['Date'])]

    # df['MatchID'] = pd.Series([str(x) for x in range(len(df))])
    # df.set_index('MatchID', inplace=True)

    df['FTHG'] = df['FTHG'].astype(int)
    df['FTAG'] = df['FTAG'].astype(int)
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

def combineAllMatches(cleanedFolderPath, finalPath):
    dfList = []
    for year in range(1993, 2019):
        file = '%s-%s.csv' % (year, year + 1)
        path = ntpath.join(cleanedFolderPath, file)
        df = pd.read_csv(path)
        # df.set_index('MatchID', inplace=True)
        dfList.append(df)
    df = pd.concat(dfList, ignore_index=True, sort=False)
    df.to_csv(ntpath.join(finalPath, 'final.csv'), index=False)

def getMatchResultsAgainst(filePath):
    teamDetail, matchDetail = {}, {}
    matchDetailColumns = [
        'HT_win_rate_against',
        'AT_win_rate_against'
    ]

    for item in matchDetailColumns:
        matchDetail[item] = []

    df = pd.read_csv(filePath)
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

    df['HT_win_rate_against'] = pd.Series(matchDetail['HT_win_rate_against'], index=df.index)
    df['AT_win_rate_against'] = pd.Series(matchDetail['AT_win_rate_against'], index=df.index)
    df.to_csv(filePath, index=False)

if __name__ == "__main__":
    RAW_DATA_FILE_PATH = 'data/raw'
    CLEANED_DATA_FILE_PATH = 'data/cleaned'
    OVA_FILE_PATH = 'data/OVAs'
    FINAL_PATH = 'data'


    # 1. From raw data, remove all data but these columns below.
    # Produces: cleaned data csv located in CLEANED_DATA_FILE_PATH
    columns = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    cleanAll(RAW_DATA_FILE_PATH, CLEANED_DATA_FILE_PATH, columns)

    # 2. From 1, add Overall Rating columns
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH. Now all cleaned csv from 2006-2019 have OVA column. 
    mergeOVAToCleanedAll(OVA_FILE_PATH, CLEANED_DATA_FILE_PATH)

    # 3. From 2, add current status columns (current point, current goal for,against,difference, match played, losing/winning streaks, last 5 games)
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH. Now all cleaned csv from 1993-2019 have additinoal columns
    addCurrentDetailsAll(CLEANED_DATA_FILE_PATH)

    # 4. From 3, merge all csv files from 1993 to 2018 together
    # Produces: new csv file under FINAL_PATH as 'final.csv'
    combineAllMatches(CLEANED_DATA_FILE_PATH, FINAL_PATH)

    # 4. From 4, get all head-to-head results (match results against the other team over time)
    # Produces: editted final.csv file under FINAL_PATH
    getMatchResultsAgainst(ntpath.join(FINAL_PATH, 'final.csv'))