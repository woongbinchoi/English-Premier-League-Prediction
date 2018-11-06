from sofifaScraper import mergeOVAToCleanedAll, scrapeTeamOVAAll
from currentStatus import addCurrentDetailsAll, addCurrentDetails
from cleanData import cleanAll, combineMatches, getMatchResultsAgainst, removeGoalScores, copy_csv
from predict import getCLF, prepare_data, predict_next_round
from matchHistory import getCurrentFixtures
from rankings import getRankings, getRankingsAll
import pandas as pd
import numpy as np
import os


#Constants
DATA_PATH = 'data'
RAW_DATA_FILE_PATH = os.path.join(DATA_PATH,'raw')
RAW_DATA_FILE_PATH_CURRENT = os.path.join(RAW_DATA_FILE_PATH, '2018-2019.csv')
OVA_FILE_PATH = os.path.join(DATA_PATH,'OVAs')
STANDINGS_PATH = os.path.join(DATA_PATH, 'standings')
STATISTICS_PATH = os.path.join(DATA_PATH,'statistics')
RAW_CLEANED_DATA_FILE_PATH = os.path.join(DATA_PATH,'raw_cleaned')
RAW_CLEANED_DATA_FILE_PATH_CURRENT = os.path.join(RAW_CLEANED_DATA_FILE_PATH, '2018-2019.csv')
CLEANED_DATA_FILE_PATH = os.path.join(DATA_PATH,'cleaned')
CLEANED_DATA_FILE_PATH_CURRENT = os.path.join(CLEANED_DATA_FILE_PATH, '2018-2019.csv')


FINAL_FILE = os.path.join(DATA_PATH, 'final.csv')
CLF_FILE = os.path.join(DATA_PATH, 'best_clf.joblib')
CONFIDENCE_FILE = os.path.join(STATISTICS_PATH, 'model_confidence.csv')
PREDICTION_FILE = os.path.join(STATISTICS_PATH, 'prediction_result.csv')
PRED_RANKING_FILE = os.path.join(STATISTICS_PATH, 'prediction_ranking.csv')



#TODO: need to make current year constant
current_year = 2018

if __name__ == "__main__":
    # Things that are manually done still...
    # 1. OVA data from SOFIFASCRAPER: To automate this, I need to run "scrapeTeamOVAAll" from 
    #    "sofifaScraper.py" before I call mergeOVATOCleanedAll. (Warning: This takes a long time to run)
#    scrapeTeamOVAAll(OVA_FILE_PATH, 2006, 2018)
    # 2. Manaually bring result data from http://www.football-data.co.uk/englandm.php
    #    This can be also done by calling "getCurrentFixtures" from matchHistory.py
#    getCurrentFixtures(RAW_DATA_FILE_PATH_CURRENT)
    # 3. past standing data from rankings: To automate this, I need to run "getRankings" from 
    #    "rankings.py" before I call everything.
    # getRankingsAll(1993, 2019, RAW_CLEANED_DATA_FILE_PATH, STANDINGS_PATH)
    
    # 1. From raw data, remove all data but these columns below.
    # Produces: cleaned data csv located in CLEANED_DATA_FILE_PATH
    columns = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    cleanAll(RAW_DATA_FILE_PATH, RAW_CLEANED_DATA_FILE_PATH, columns, 1993, 2018)

    # 2. From 1, add Overall Rating columns
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH. Now all cleaned csv from 2006-2019 have OVA column. 
    mergeOVAToCleanedAll(OVA_FILE_PATH, RAW_CLEANED_DATA_FILE_PATH, 2006, 2018)
    
    # 3. From 2, copy cleaned raw data to cleaned data for prediction purpose
    # Produces: copy csv from RAW_CLEANED_DATA_FILE_PATH to CLEANED_DATA_FILE_PATH
    copy_csv(RAW_CLEANED_DATA_FILE_PATH, CLEANED_DATA_FILE_PATH)

    # 4. From 3, add current status columns (current point, current goal for,against,difference, match played, losing/winning streaks, last 5 games)
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH. Now all cleaned csv from 1993-2019 have additinoal columns
    addCurrentDetailsAll(CLEANED_DATA_FILE_PATH, CLEANED_DATA_FILE_PATH, STANDINGS_PATH, 1993, 2018)

    # 5. From 4, merge all csv files from startYear to endYear together. 
    # FOR NOW, I only collect data from 2006 because sofifa only provides ova data from 2006
    # Produces: new csv file on FINAL_FILE
    combineMatches(CLEANED_DATA_FILE_PATH, FINAL_FILE, 2006, 2018)

    # 6. From 5, get all head-to-head results (match results against the other team over time)
    # Produces: editted final.csv file under DATA_PATH
    getMatchResultsAgainst(FINAL_FILE, CLEANED_DATA_FILE_PATH, DATA_PATH, 1993, 2018)

    # 7. Once all data is aggregated, we can now build a classifer that make preidctions. 
    # If 'recalculate' is set True, it runs multiple classifiers on this data, 
    # and do some grid search on it if necessary, and finally generates 'model confidence.csv' that records confidence score of each classifier.
    # If 'recalculate' is set False, and if clf_file exists, then it simply loads the clf from clf_file.
    # Produces: returns the best clf.
    best_clf = getCLF(FINAL_FILE, CONFIDENCE_FILE, CLF_FILE, recalculate=False)

#    # TODO: What if I only use the current 5 years of data or something?

    # 8. Now we make prediction. This process is done by first predicting the upcoming round, then aggregate the result, then predict the next,
    # and repeat the process until there are no more games to predict. "predict_next_round" also produces prediction probabilities
    # for each matches on stat_path. 
    #  - 1. predict_next_round predicts next round and save the result in RAW_CLEANED_DATA_FILE_PATH_CURRENT.
    #  - 2. addCurrentDetails, as its name suggests, it adds current details.
    #  - 3. combineMatches combine all matches from 2006 to 2018
    #  - 4. getMatchResultsAgainst adds head-to-head results between two teams for each match
    is_first = True
    while predict_next_round(best_clf, FINAL_FILE, RAW_CLEANED_DATA_FILE_PATH_CURRENT,
                             statistics=True, stat_path=PREDICTION_FILE, first=is_first):
        addCurrentDetails(RAW_CLEANED_DATA_FILE_PATH_CURRENT, CLEANED_DATA_FILE_PATH_CURRENT, STANDINGS_PATH)
        combineMatches(CLEANED_DATA_FILE_PATH, DATA_PATH, 2006, 2018)
        getMatchResultsAgainst(FINAL_FILE, CLEANED_DATA_FILE_PATH, DATA_PATH)
        is_first = False
    
    # 9. Now prediction is done. Produce a season standing with using the prediction result.
    getRankings(PREDICTION_FILE, PRED_RANKING_FILE, include_prediction=True)
        