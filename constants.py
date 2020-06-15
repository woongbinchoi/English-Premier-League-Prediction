import datetime
import os

def get_current_season():
    now = datetime.datetime.now()
    # By July, fixture of the season should be available.
    new_season_start = datetime.datetime(now.year, 7, 1)
    return now.year if now > new_season_start else now.year - 1

# Constants
CURRENT_YEAR = get_current_season()
CURRENT_FILE = '{}-{}.csv'.format(CURRENT_YEAR, CURRENT_YEAR + 1)

DATA_PATH = 'data'

RAW_DATA_FILE_PATH = 'data/raw/results'
OVA_FILE_PATH =      'data/raw/OVAs'

STANDINGS_PATH =             'data/cleaned/standings'
RAW_CLEANED_DATA_FILE_PATH = 'data/cleaned/results'

CLEANED_DATA_FILE_PATH = 'data/train_data/results'
FINAL_FILE =             'data/train_data/final.csv'
CLF_FILE =               'data/train_data/best_clf.joblib'
CONFIDENCE_FILE =        'data/train_data/model_confidence.csv'

STATISTICS_PATH = 'data/statistics'
DATABASE_PATH =   'data/database.db'

RAW_DATA_FILE_PATH_CURRENT =         os.path.join(RAW_DATA_FILE_PATH, CURRENT_FILE)
RAW_CLEANED_DATA_FILE_PATH_CURRENT = os.path.join(RAW_CLEANED_DATA_FILE_PATH, CURRENT_FILE)
CLEANED_DATA_FILE_PATH_CURRENT =     os.path.join(CLEANED_DATA_FILE_PATH, CURRENT_FILE)

PRED_RANKING_ROUND_PATH =         os.path.join(STATISTICS_PATH, 'round_rankings')
PREDICTION_FILE =                 os.path.join(STATISTICS_PATH, 'prediction_result.csv')
PRED_RANKING_FILE =               os.path.join(STATISTICS_PATH, 'prediction_ranking.csv')
PRED_RANKING_ROUND_SUMMARY_FILE = os.path.join(STATISTICS_PATH, 'round_rankings_summary.csv')

SCRAPER_TIMEOUT = 5
SCRAPER_SLEEP = 1
