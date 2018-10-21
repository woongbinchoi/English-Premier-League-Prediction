import ntpath
from sofifaScraper import mergeOVAToCleanedAll
from currentStatus import addCurrentDetailsAll
from cleanData import cleanAll, combineMatches, getMatchResultsAgainst, removeGoalScores
from predict import getCLF


#Constants
RAW_DATA_FILE_PATH = 'data/raw'
CLEANED_DATA_FILE_PATH = 'data/cleaned'
OVA_FILE_PATH = 'data/OVAs'
FINAL_PATH = 'data'
FINAL_FILE = ntpath.join(FINAL_PATH, 'final.csv')
CONFIDENCE_FILE = ntpath.join(FINAL_PATH, 'model_confidence.csv')




if __name__ == "__main__":
    # Things that are manually done still...
    # 1. OVA data from SOFIFASCRAPER: To automate this, I need to run "scrapeTeamOVAAll" from 
    #    "sofifaScraper.py" before I call mergeOVATOCleanedAll. (Warning: This takes a long time to run)
    # 2. Manaually bring result data from http://www.football-data.co.uk/englandm.php
    
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

    # 4. From 3, merge all csv files from startYear to endYear together
    # Produces: new csv file under FINAL_PATH as 'final.csv'
    combineMatches(CLEANED_DATA_FILE_PATH, FINAL_PATH, 2006, 2019)

    # 5. From 4, get all head-to-head results (match results against the other team over time)
    # Produces: editted final.csv file under FINAL_PATH
    getMatchResultsAgainst(FINAL_FILE, CLEANED_DATA_FILE_PATH, FINAL_PATH)

    # 6. From 5, remove goal score, which we don't need for prediction
    # Produces: editted final.csv file under FINAL_PATH
    removeGoalScores(FINAL_FILE)

    # 7. Once all data is aggregated, we can now build a classifer that make preidctions. Call this function to run multiple classifiers
    #    on this data, and do some grid search on it if necessary. Finally get clf that gives the best prediction accuracy.
    # Produces: returns the best clf. It also generates 'model confidence.csv' that records confidence score of each classifier.
    BEST_CLF = getCLF(FINAL_FILE, CONFIDENCE_FILE)
    
    print(BEST_CLF)