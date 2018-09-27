import ntpath
import os
import pandas as pd
from sofifaScraper import mergeOVAToCleanedAll
from currentStatus import addCurrentDetailsAll


# clean the original raw data by storing only the columns that we need, and removing the rest.
def clean(fromPath, toPath, columns):
    print("Cleaning ", fromPath, "...")
    df = pd.read_csv(fromPath, error_bad_lines=False)
    df = df[columns]
    df = df[pd.notnull(df['Date'])]

    df['MatchID'] = pd.Series([str(x) for x in range(len(df))])
    df.set_index('MatchID', inplace=True)

    df['FTHG'] = df['FTHG'].astype(int)
    df['FTAG'] = df['FTAG'].astype(int)
    
    head, _ = ntpath.split(toPath)
    if not os.path.exists(head):
        os.makedirs(head)
    df.to_csv(toPath)

def cleanAll(fromFolder, toFolder, columns):
    for year in range(1993, 2019):
        csvFile = '%s-%s.csv' % (year, year + 1)
        frompath = ntpath.join(fromFolder, csvFile)
        topath = ntpath.join(toFolder, csvFile)
        clean(frompath, topath, columns)

if __name__ == "__main__":
    RAW_DATA_FILE_PATH = 'data/raw'
    CLEANED_DATA_FILE_PATH = 'data/cleaned'
    OVA_FILE_PATH = 'data/OVAs'

    # 1. From raw data, remove all data but these columns below.
    # Produces: cleaned data csv located in CLEANED_DATA_FILE_PATH
    columns = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    cleanAll(RAW_DATA_FILE_PATH, CLEANED_DATA_FILE_PATH, columns)

    # 2. From 1, add Overall Rating columns
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH. Now all cleaned csv from 2006-2019 have OVA column. 
    mergeOVAToCleanedAll(OVA_FILE_PATH, CLEANED_DATA_FILE_PATH)

    # 3. From 2, add current status columns (current point, current goal for,against,difference, match played)
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH. Now all cleaned csv from 1993-2019 have additinoal columns
    addCurrentDetailsAll(CLEANED_DATA_FILE_PATH)
    