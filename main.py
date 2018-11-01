import ntpath
from sofifaScraper import mergeOVAToCleanedAll, scrapeTeamOVAAll
from currentStatus import addCurrentDetailsAll
from cleanData import cleanAll, combineMatches, getMatchResultsAgainst, removeGoalScores, copy_csv
from predict import getCLF, prepare_data, predict_next_round
from matchHistory import getCurrentFixtures
import pandas as pd
import numpy as np
import os


#Constants
DATA_PATH = 'data'
RAW_DATA_FILE_PATH = os.path.join(DATA_PATH,'raw')
RAW_CLEANED_DATA_FILE_PATH = os.path.join(DATA_PATH,'raw_cleaned')
RAW_CLEANED_DATA_FILE_PATH_CURRENT = os.path.join(RAW_CLEANED_DATA_FILE_PATH, '2018-2019.csv')
CLEANED_DATA_FILE_PATH = os.path.join(DATA_PATH,'cleaned')
OVA_FILE_PATH = os.path.join(DATA_PATH,'OVAs')
STATISTICS_PATH = os.path.join(DATA_PATH,'statistics')

FINAL_FILE = ntpath.join(DATA_PATH, 'final.csv')
CONFIDENCE_FILE = ntpath.join(STATISTICS_PATH, 'model_confidence.csv')
CLF_FILE = ntpath.join(DATA_PATH, 'best_clf.joblib')


#TODO: need to make current year constant

if __name__ == "__main__":
    # Things that are manually done still...
    # 1. OVA data from SOFIFASCRAPER: To automate this, I need to run "scrapeTeamOVAAll" from 
    #    "sofifaScraper.py" before I call mergeOVATOCleanedAll. (Warning: This takes a long time to run)
#    scrapeTeamOVAAll(OVA_FILE_PATH)
    # 2. Manaually bring result data from http://www.football-data.co.uk/englandm.php
    #    This can be also done by calling "getCurrentFixtures" from matchHistory.py
    getCurrentFixtures(RAW_DATA_FILE_PATH)
    # 3. past standing data from rankings: To automate this, I need to run "getRankings" from 
    #    "rankings.py" before I call everything.
    
    # 1. From raw data, remove all data but these columns below.
    # Produces: cleaned data csv located in CLEANED_DATA_FILE_PATH
    columns = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    cleanAll(RAW_DATA_FILE_PATH, RAW_CLEANED_DATA_FILE_PATH, columns)

    # 2. From 1, add Overall Rating columns
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH. Now all cleaned csv from 2006-2019 have OVA column. 
    mergeOVAToCleanedAll(OVA_FILE_PATH, RAW_CLEANED_DATA_FILE_PATH)
    
    # 3. From 2, copy cleaned raw data to cleaned data for prediction purpose
    # Produces: copy csv from RAW_CLEANED_DATA_FILE_PATH to CLEANED_DATA_FILE_PATH
    copy_csv(RAW_CLEANED_DATA_FILE_PATH, CLEANED_DATA_FILE_PATH)

    # 4. From 3, add current status columns (current point, current goal for,against,difference, match played, losing/winning streaks, last 5 games)
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH. Now all cleaned csv from 1993-2019 have additinoal columns
    addCurrentDetailsAll(CLEANED_DATA_FILE_PATH)

    # 5. From 4, merge all csv files from startYear to endYear together. 
    # FOR NOW, I only collect data from 2006 because sofifa only provides ova data from 2006
    # Produces: new csv file under DATA_PATH as 'final.csv'
    combineMatches(CLEANED_DATA_FILE_PATH, DATA_PATH, 2006, 2019)

    # 6. From 5, get all head-to-head results (match results against the other team over time)
    # Produces: editted final.csv file under DATA_PATH
    getMatchResultsAgainst(FINAL_FILE, CLEANED_DATA_FILE_PATH, DATA_PATH)

    # 7. Once all data is aggregated, we can now build a classifer that make preidctions. 
    # If 'recalculate' is set True, it runs multiple classifiers on this data, 
    # and do some grid search on it if necessary, and finally generates 'model confidence.csv' that records confidence score of each classifier.
    # If 'recalculate' is set False, and if clf_file exists, then it simply loads the clf from clf_file.
    # Produces: returns the best clf.
    best_clf = getCLF(FINAL_FILE, CONFIDENCE_FILE, CLF_FILE, recalculate=False)
    
    predict_next_round(best_clf, FINAL_FILE, RAW_CLEANED_DATA_FILE_PATH_CURRENT)
    
    rounds_to_predict = int(input("How many rounds do you want to make prediction?: "))
    
    # TODO: Make this loop to only do the job that is needed
    # TODO: Make it stop when all of them are predicted already
    # TODO: What if I only use the current 5 years of data or something?
    for round in range(rounds_to_predict):
        copy_csv(RAW_CLEANED_DATA_FILE_PATH, CLEANED_DATA_FILE_PATH)
        addCurrentDetailsAll(CLEANED_DATA_FILE_PATH)
        combineMatches(CLEANED_DATA_FILE_PATH, DATA_PATH, 2006, 2019)
        getMatchResultsAgainst(FINAL_FILE, CLEANED_DATA_FILE_PATH, DATA_PATH)
        predict_next_round(best_clf, FINAL_FILE, RAW_CLEANED_DATA_FILE_PATH_CURRENT)