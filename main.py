import ntpath
from sofifaScraper import mergeOVAToCleanedAll, scrapeTeamOVAAll
from currentStatus import addCurrentDetailsAll
from cleanData import cleanAll, combineMatches, getMatchResultsAgainst, removeGoalScores
from predict import getCLF, prepare_data
from matchHistory import getCurrentFixtures
import pandas as pd


#Constants
RAW_DATA_FILE_PATH = 'data/raw'
CLEANED_DATA_FILE_PATH = 'data/cleaned'
OVA_FILE_PATH = 'data/OVAs'
FINAL_PATH = 'data'
FINAL_FILE = ntpath.join(FINAL_PATH, 'final.csv')
CONFIDENCE_FILE = ntpath.join(FINAL_PATH, 'model_confidence.csv')
CLF_FILE = ntpath.join(FINAL_PATH, 'best_clf.joblib')




if __name__ == "__main__":
    # Things that are manually done still...
    # 1. OVA data from SOFIFASCRAPER: To automate this, I need to run "scrapeTeamOVAAll" from 
    #    "sofifaScraper.py" before I call mergeOVATOCleanedAll. (Warning: This takes a long time to run)
#    scrapeTeamOVAAll(OVA_FILE_PATH)
    # 2. Manaually bring result data from http://www.football-data.co.uk/englandm.php
    #    This can be also done by calling "getCurrentFixtures" from matchHistory.py
#    getCurrentFixtures(RAW_DATA_FILE_PATH)
    # 3. past standing data from rankings: To automate this, I need to run "getRankings" from 
    #    "rankings.py" before I call everything.
    
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

    # 4. From 3, merge all csv files from startYear to endYear together. 
    # FOR NOW, I only collect data from 2006 because sofifa only provides ova data from 2006
    # Produces: new csv file under FINAL_PATH as 'final.csv'
    combineMatches(CLEANED_DATA_FILE_PATH, FINAL_PATH, 2006, 2019)

    # 5. From 4, get all head-to-head results (match results against the other team over time)
    # Produces: editted final.csv file under FINAL_PATH
    getMatchResultsAgainst(FINAL_FILE, CLEANED_DATA_FILE_PATH, FINAL_PATH)

    # 6. From 5, remove goal score, which we don't need for prediction
    # Produces: editted final.csv file under FINAL_PATH
    removeGoalScores(FINAL_FILE)

    # 7. Once all data is aggregated, we can now build a classifer that make preidctions. 
    # If 'recalculate' is set True, it runs multiple classifiers on this data, 
    # and do some grid search on it if necessary, and finally generates 'model confidence.csv' that records confidence score of each classifier.
    # If 'recalculate' is set False, and if clf_file exists, then it simply loads the clf from clf_file.
    # Produces: returns the best clf.
    BEST_CLF = getCLF(FINAL_FILE, CONFIDENCE_FILE, CLF_FILE, recalculate=False)
    print("GET_CLF: ", BEST_CLF)
    
    
#    
#BEST_CLF = getCLF(FINAL_FILE, CONFIDENCE_FILE, CLF_FILE, recalculate=False)
#
#df = pd.read_csv('data/final.csv')
#df = df.loc[(df['FTR'] == 'X')]
#df = df.loc[(df['HT_goal_for']) == (df['HT_goal_for'])]
#Home = df['HomeTeam'].tolist()
#Away = df['AwayTeam'].tolist()
#df = prepare_data(df, drop_na=False)
#df = df.drop(columns=['FTR'])
#
#prediction = BEST_CLF.predict(df).tolist()
#prediction_probability = BEST_CLF.predict_proba(df).tolist()
#
#print("Home       Away       Predict       Probability")
#for (HT, AT, pred, pred_prob) in zip(Home, Away, prediction, prediction_probability):
#    print("{}      {}      {}      {}".format(HT, AT, HT if pred == "H" else AT, max(pred_prob)))