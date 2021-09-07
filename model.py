from sofifa_scraper import merge_ova_to_cleaned_all, scrape_team_ova_all
from constants import (
    CURRENT_YEAR,
    CURRENT_FILE,
    DATA_PATH,
    RAW_DATA_FILE_PATH,
    OVA_FILE_PATH,
    STANDINGS_PATH,
    STATISTICS_PATH,
    RAW_CLEANED_DATA_FILE_PATH,
    CLEANED_DATA_FILE_PATH,
    DATABASE_PATH,
    FINAL_FILE,
    CLF_FILE,
    CONFIDENCE_FILE,
    RAW_DATA_FILE_PATH_CURRENT,
    RAW_CLEANED_DATA_FILE_PATH_CURRENT,
    CLEANED_DATA_FILE_PATH_CURRENT,
    PRED_RANKING_ROUND_PATH,
    PREDICTION_FILE,
    PRED_RANKING_FILE,
    PRED_RANKING_ROUND_SUMMARY_FILE
)
from current_status import add_current_details_all, add_current_details
from clean_data import (
    clean_all,
    combine_matches,
    get_match_results_against,
    remove_goal_scores,
    save_new_data_to_database,
    save_summary_to_database,
)
from helpers import (
    copy_csv,
    remove_directory,
)
from predict import get_clf, prepare_data, predict_next_round
from match_history import get_fixtures, get_current_fixtures
from rankings import get_rankings, get_rankings_all
import pandas as pd
import numpy as np
import os
import datetime
import argparse


def magic(should_train=True, should_scrape=False, data_year_available_from=1993, data_year_collect_from=2006):
    # Function(s) that don't have to be executed every time

    # 1. OVA data from sofifa_scraper (Warning: This takes a long time to run)
    #   SOFIFA updates their stat two or three times every month, but they don't change data much
    # Uncomment below to scrape team overall stat data
    if should_scrape:
        scrape_team_ova_all(OVA_FILE_PATH, data_year_collect_from, CURRENT_YEAR)

    # Preprocessing

    # Preprocessing-1. Latest premier league results 
    # This data can also be retrieved from http://www.football-data.co.uk/englandm.php
    # Uncomment below to get the latest match results
    get_fixtures(RAW_DATA_FILE_PATH, data_year_available_from, CURRENT_YEAR)
    get_current_fixtures(RAW_DATA_FILE_PATH_CURRENT)

    # Run the functions below to start generating necessary data

    # 1. From raw data, remove all data but the selected columns.
    # Produces: cleaned data csv located in CLEANED_DATA_FILE_PATH
    clean_all(RAW_DATA_FILE_PATH, RAW_CLEANED_DATA_FILE_PATH, data_year_available_from, CURRENT_YEAR)

    # Preprocessing-2. Standings (from 1993 to curent year)
    # Uncomment below to run the function
    get_rankings_all(data_year_available_from, CURRENT_YEAR, RAW_CLEANED_DATA_FILE_PATH, STANDINGS_PATH)

    # 2. From 1, add Overall Rating columns
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH. Now all cleaned csv from 2006-2018 have OVA column. 
    merge_ova_to_cleaned_all(OVA_FILE_PATH, RAW_CLEANED_DATA_FILE_PATH, data_year_collect_from, CURRENT_YEAR)

    # 3. From 2, copy cleaned raw data to cleaned data for prediction purpose
    # Produces: copy csv from RAW_CLEANED_DATA_FILE_PATH to CLEANED_DATA_FILE_PATH
    copy_csv(RAW_CLEANED_DATA_FILE_PATH, CLEANED_DATA_FILE_PATH)

    # 4. From 3, add current status columns (current point, current goal for,against,difference, match played, losing/winning streaks, last 5 games)
    # Produces: cleaned csv modified, located in CLEANED_DATA_FILE_PATH. Now all cleaned csv from 1993-2018 have additional columns
    add_current_details_all(CLEANED_DATA_FILE_PATH, CLEANED_DATA_FILE_PATH, STANDINGS_PATH, data_year_available_from, CURRENT_YEAR, data_year_available_from)

    # 5. From 4, merge all csv files from startYear to endYear together. 
    # FOR NOW, I only collect data from 2006 because sofifa only provides ova data from 2006, and model tends to perform better with this approach
    # Produces: new csv file on FINAL_FILE
    combine_matches(CLEANED_DATA_FILE_PATH, FINAL_FILE, data_year_collect_from, CURRENT_YEAR)

    # 6. From 5, get all head-to-head results (match results against the other team over time)
    # Produces: editted final.csv file under DATA_PATH
    get_match_results_against(FINAL_FILE, CLEANED_DATA_FILE_PATH, DATA_PATH, data_year_available_from, CURRENT_YEAR)

    # 7. Once all data is aggregated, we can now build a classifer that make preidctions. 
    # If 'recalculate' is set True, it runs multiple classifiers on this data, 
    # and do some grid search on it if necessary, and finally generates 'model confidence.csv' that records confidence score of each classifier.
    # If 'recalculate' is set False, and if clf_file exists, then it simply loads the clf from clf_file.
    # Produces: returns the best clf.
    best_clf, _, best_clf_average = get_clf(FINAL_FILE, CONFIDENCE_FILE, CLF_FILE, recalculate=should_train)
    
    # 8. Now we make prediction. This process is done by first predicting the upcoming round, then aggregate the result, then predict the next,
    # and repeat the process until there are no more games to predict. "predict_next_round" also produces prediction probabilities
    # for each matches on stat_path. 
    #  - 1. predict_next_round predicts next round and save the result in RAW_CLEANED_DATA_FILE_PATH_CURRENT.
    #  - 2. add_current_details, as its name suggests, it adds current details.
    #  - 3. combine_matches combine all matches from 2006 to 2018
    #  - 4. get_match_results_against adds head-to-head results between two teams for each match
    is_first = True

    # First save current ranking before predicting results
    remove_directory(STATISTICS_PATH)
    now = datetime.datetime.now().date().strftime('%Y-%m-%d')
    pred_ranking_round_file = os.path.join(PRED_RANKING_ROUND_PATH, 'prediction_ranking_{}.csv'.format(now))
    get_rankings(RAW_CLEANED_DATA_FILE_PATH_CURRENT, pred_ranking_round_file, include_prediction=True, predicted_date_so_far=now, ranking_summary_file=PRED_RANKING_ROUND_SUMMARY_FILE)

    while True:
        is_next_round, date = predict_next_round(best_clf, FINAL_FILE, RAW_CLEANED_DATA_FILE_PATH_CURRENT, statistics=True, stat_path=PREDICTION_FILE, first=is_first)
        if not is_next_round:
            break
        add_current_details(RAW_CLEANED_DATA_FILE_PATH_CURRENT, CLEANED_DATA_FILE_PATH_CURRENT, STANDINGS_PATH, data_year_available_from)
        combine_matches(CLEANED_DATA_FILE_PATH, FINAL_FILE, data_year_collect_from, CURRENT_YEAR)
        get_match_results_against(FINAL_FILE, CLEANED_DATA_FILE_PATH, DATA_PATH, data_year_available_from, CURRENT_YEAR)
        pred_ranking_round_file = os.path.join(PRED_RANKING_ROUND_PATH, 'prediction_ranking_{}.csv'.format(date))
        get_rankings(PREDICTION_FILE, pred_ranking_round_file, include_prediction=True, predicted_date_so_far=date, ranking_summary_file=PRED_RANKING_ROUND_SUMMARY_FILE)
        is_first = False

    # 9. Now prediction is done. Produce a season standing with using the prediction result.
    winning_team = get_rankings(PREDICTION_FILE, PRED_RANKING_FILE, include_prediction=True)
    
    # 10. Put previous results, prediction results, standing predictions to the database
    save_new_data_to_database(DATABASE_PATH, FINAL_FILE, PREDICTION_FILE, PRED_RANKING_ROUND_SUMMARY_FILE)
    
    # 11. Summary to database
    if should_train:
        save_summary_to_database(DATABASE_PATH, best_clf_average, winning_team)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--skip_train',
        action='store_true',
        help='indicate whether to skip training a new model before prediction')
    parser.add_argument(
        '--skip_scrape',
        action='store_true',
        help='indicate whether to skip scraping ova from sofifa')

    args = parser.parse_args()
    magic(should_train=not args.skip_train, should_scrape=not args.skip_scrape)
