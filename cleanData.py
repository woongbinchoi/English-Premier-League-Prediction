import ntpath
import os
import pandas as pd


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
    columns = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    cleanAll('data/raw', 'data/cleaned', columns)

