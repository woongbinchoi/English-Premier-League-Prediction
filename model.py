from sofifaScraper import mergeOVAToCleanedAll, scrapeTeamOVAAll
from currentStatus import addCurrentDetailsAll, addCurrentDetails, getCurrentSeason
from cleanData import cleanAll, combineMatches, getMatchResultsAgainst, removeGoalScores, copy_csv, remove_directory, saveNewDataToDatabase
from predict import getCLF, prepare_data, predict_next_round
from matchHistory import getCurrentFixtures
from rankings import getRankings, getRankingsAll
import pandas as pd
import numpy as np
import os
import datetime


def magic(should_train=True, data_year_available_from=1993, data_year_collect_from=2006):
    # Constants
    current_year = getCurrentSeason()
    CURRENT_FILE = '{}-{}.csv'.format(current_year, current_year + 1)
    columns = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']


    # Paths
    DATA_PATH = 'data'

    RAW_DATA_FILE_PATH = os.path.join(DATA_PATH,'raw')
    OVA_FILE_PATH = os.path.join(DATA_PATH,'OVAs')
    STANDINGS_PATH = os.path.join(DATA_PATH, 'standings')
    STATISTICS_PATH = os.path.join(DATA_PATH,'statistics')
    RAW_CLEANED_DATA_FILE_PATH = os.path.join(DATA_PATH,'raw_cleaned')
    CLEANED_DATA_FILE_PATH = os.path.join(DATA_PATH,'cleaned')
    DATABASE_PATH = os.path.join(DATA_PATH, 'database.db')
    FINAL_FILE = os.path.join(DATA_PATH, 'final.csv')
    CLF_FILE = os.path.join(DATA_PATH, 'best_clf.joblib')
    CONFIDENCE_FILE = os.path.join(DATA_PATH, 'model_confidence.csv')

    RAW_DATA_FILE_PATH_CURRENT = os.path.join(RAW_DATA_FILE_PATH, CURRENT_FILE)
    RAW_CLEANED_DATA_FILE_PATH_CURRENT = os.path.join(RAW_CLEANED_DATA_FILE_PATH, CURRENT_FILE)
    CLEANED_DATA_FILE_PATH_CURRENT = os.path.join(CLEANED_DATA_FILE_PATH, CURRENT_FILE)
    PRED_RANKING_ROUND_PATH = os.path.join(STATISTICS_PATH, 'round_rankings')
    PREDICTION_FILE = os.path.join(STATISTICS_PATH, 'prediction_result.csv')
    PRED_RANKING_FILE = os.path.join(STATISTICS_PATH, 'prediction_ranking.csv')
    PRED_RANKING_ROUND_SUMMARY_FILE = os.path.join(STATISTICS_PATH, 'round_rankings_summary.csv')
    CURRENT_STANDINGS_FILE = os.path.join(STANDINGS_PATH, CURRENT_FILE)


    # Function(s) that don't have to be executed every time

    # 1. OVA data from SOFIFASCRAPER (Warning: This takes a long time to run)
    #   SOFIFA updates their stat two or three times every month, but they don't change data much
    # Uncomment below to scrape team overall stat data
    scrapeTeamOVAAll(OVA_FILE_PATH, data_year_collect_from, current_year)


    # Preprocessing

    # 1. Latest premier league results 
    # This data can also be retrieved from http://www.football-data.co.uk/englandm.php
    # Uncomment below to get the latest match results
    getCurrentFixtures(RAW_DATA_FILE_PATH_CURRENT)

    # 2. Standings (from 1993 to curent year)
    # Uncomment below to run the function
    getRankingsAll(data_year_available_from, current_year, RAW_CLEANED_DATA_FILE_PATH, STANDINGS_PATH)
    

    # Run the functions below to start generating necessary data

    # 1. From raw data, remove all data but the selected columns.
    # Produces: cleaned data csv located in CLEANED_DATA_FILE_PATH
    cleanAll(RAW_DATA_FILE_PATH, RAW_CLEANED_DATA_FILE_PATH, columns, data_year_available_from, current_year)

    # 2. From 1, add Overall Rating columns
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH. Now all cleaned csv from 2006-2018 have OVA column. 
    mergeOVAToCleanedAll(OVA_FILE_PATH, RAW_CLEANED_DATA_FILE_PATH, data_year_collect_from, current_year)
    
    # 3. From 2, copy cleaned raw data to cleaned data for prediction purpose
    # Produces: copy csv from RAW_CLEANED_DATA_FILE_PATH to CLEANED_DATA_FILE_PATH
    copy_csv(RAW_CLEANED_DATA_FILE_PATH, CLEANED_DATA_FILE_PATH)

    # 4. From 3, add current status columns (current point, current goal for,against,difference, match played, losing/winning streaks, last 5 games)
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH. Now all cleaned csv from 1993-2018 have additional columns
    addCurrentDetailsAll(CLEANED_DATA_FILE_PATH, CLEANED_DATA_FILE_PATH, STANDINGS_PATH, data_year_available_from, current_year, data_year_available_from)

    # 5. From 4, merge all csv files from startYear to endYear together. 
    # FOR NOW, I only collect data from 2006 because sofifa only provides ova data from 2006, and model tends to perform better with this approach
    # Produces: new csv file on FINAL_FILE
    combineMatches(CLEANED_DATA_FILE_PATH, FINAL_FILE, data_year_collect_from, current_year)

    # 6. From 5, get all head-to-head results (match results against the other team over time)
    # Produces: editted final.csv file under DATA_PATH
    getMatchResultsAgainst(FINAL_FILE, CLEANED_DATA_FILE_PATH, DATA_PATH, data_year_available_from, current_year)

    # 7. Once all data is aggregated, we can now build a classifer that make preidctions. 
    # If 'recalculate' is set True, it runs multiple classifiers on this data, 
    # and do some grid search on it if necessary, and finally generates 'model confidence.csv' that records confidence score of each classifier.
    # If 'recalculate' is set False, and if clf_file exists, then it simply loads the clf from clf_file.
    # Produces: returns the best clf.
    best_clf, y_results = getCLF(FINAL_FILE, CONFIDENCE_FILE, CLF_FILE, recalculate=should_train)
    
    # 8. Now we make prediction. This process is done by first predicting the upcoming round, then aggregate the result, then predict the next,
    # and repeat the process until there are no more games to predict. "predict_next_round" also produces prediction probabilities
    # for each matches on stat_path. 
    #  - 1. predict_next_round predicts next round and save the result in RAW_CLEANED_DATA_FILE_PATH_CURRENT.
    #  - 2. addCurrentDetails, as its name suggests, it adds current details.
    #  - 3. combineMatches combine all matches from 2006 to 2018
    #  - 4. getMatchResultsAgainst adds head-to-head results between two teams for each match
    is_first = True
    
    # First save current ranking before predicting results
    remove_directory(STATISTICS_PATH)
    now = datetime.datetime.now().date().strftime('%Y-%m-%d')
    pred_ranking_round_file = os.path.join(PRED_RANKING_ROUND_PATH, 'prediction_ranking_{}.csv'.format(now))
    getRankings(RAW_CLEANED_DATA_FILE_PATH_CURRENT, pred_ranking_round_file, include_prediction=True, predicted_date_so_far=now, ranking_summary_file=PRED_RANKING_ROUND_SUMMARY_FILE)
    
    while True:
        isNextRound, date = predict_next_round(best_clf, FINAL_FILE, RAW_CLEANED_DATA_FILE_PATH_CURRENT, statistics=True, stat_path=PREDICTION_FILE, first=is_first)
        if not isNextRound:
            break
        addCurrentDetails(RAW_CLEANED_DATA_FILE_PATH_CURRENT, CLEANED_DATA_FILE_PATH_CURRENT, STANDINGS_PATH, data_year_available_from)
        combineMatches(CLEANED_DATA_FILE_PATH, FINAL_FILE, data_year_collect_from, current_year)
        getMatchResultsAgainst(FINAL_FILE, CLEANED_DATA_FILE_PATH, DATA_PATH, data_year_available_from, current_year)
        pred_ranking_round_file = os.path.join(PRED_RANKING_ROUND_PATH, 'prediction_ranking_{}.csv'.format(date))
        getRankings(PREDICTION_FILE, pred_ranking_round_file, include_prediction=True, predicted_date_so_far=date, ranking_summary_file=PRED_RANKING_ROUND_SUMMARY_FILE)
        is_first = False
    
    # 9. Now prediction is done. Produce a season standing with using the prediction result.
    getRankings(PREDICTION_FILE, PRED_RANKING_FILE, include_prediction=True)
    
    # 10. Put previous results, prediction results, standing predictions to the database
    saveNewDataToDatabase(DATABASE_PATH, FINAL_FILE, PREDICTION_FILE, PRED_RANKING_ROUND_SUMMARY_FILE)
    


if __name__ == "__main__":
    magic()

    