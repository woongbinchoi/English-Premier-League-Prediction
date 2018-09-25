import ntpath
import os
import pandas as pd


# clean the original raw data by storing only the columns that we need, and removing the rest.
def clean(path, columns):
    print("Cleaning ", path, "...")
    df = pd.read_csv(path, error_bad_lines=False)
    df = df[columns]
    df = df[pd.notnull(df['Date'])]

    df['MatchID'] = pd.Series([str(x) for x in range(len(df))])
    df.set_index('MatchID', inplace=True)

    df['FTHG'] = df['FTHG'].astype(int)
    df['FTAG'] = df['FTAG'].astype(int)
    
    fileName = ntpath.basename(path)
    head, _ = ntpath.split(path)
    newDir = ntpath.join(head, 'cleaned')
    if not os.path.exists(newDir):
        os.makedirs(newDir)
    
    newfilePath = ntpath.join(newDir, fileName)
    df.to_csv(newfilePath)



if __name__ == "__main__":
    # columns = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    
    # for year in range(1993, 2019):
    #     path = 'data/%s-%s.csv' % (year, year + 1)
    #     clean(path, columns)

