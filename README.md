# English-Premier-League-Prediction
Apply machine learning to predict English Premier League soccer match.

[Demo App](https://epl-client.herokuapp.com/)



&nbsp;
&nbsp;


## To Run
> python3 model.py

***Warning***: Few python packages required to run the script. Install them all, or use a 3rd party IDE (such as spyder) that pre-installs these packages by default. Few of the packages required are:
- brew cask install chromedriver
- brew install libomp
- pip3 install xgboost
- pip3 install selenium



&nbsp;
&nbsp;

## Scripts
#### 1. clean_data.py
- Includes necessary helper functions to process raw data
#### 2. current_status.py
- Collects and adds more details to the processed raw data
- current/past standings, goals for/against/differences, etc.
#### 3. match_history.py
- Collects the latest match results
#### 4. rankings.py
- Calculate league points and generate standings
#### 5. sofifa_scraper.py
- Scrape overall team stat from FIFA
#### 6. predict.py
- With using processed data, train a ML model to predict future results
#### 7. model.py
- I/O file where the functions from the above files are actually executed

&nbsp;
&nbsp;



## Data
#### 1. data/raw/OVAs (directory)
- scraped overall team stat data
#### 2. data/cleaned/standings (directory)
- historical standing results calculated in rankings.py
#### 3. data/raw/results (directory)
- manually collected historical data of match outcomes
- latest match outcomes of the current season
#### 4. data/cleaned/results (directory)
- data extracted from data/raw/results
#### 5. data/train_data/results (directory)
- data processed from data/cleaned/results
#### 6. data/statistics (directory)
1. data/statistics/round_rankings (directory)
	- standings calculated based on the predicted match outcomes
	- each file in the directory has a date included in its name. It provides predicted standing outcomes at the denoted date
2. data/statistics/prediction_ranking.csv
	- predicted standing at the end of the season
3. data/statistics/prediction_result.csv
	- individual predicted match outcomes
4. data/statistics/round_rankings_summary.csv
	- predicted standing summary over the course of the season
#### 7. data/statistics/best_clf.joblib
- disk cache of classifier that gives the best accuracy of prediction
#### 8. data/database.db
- sql database that stores previous match outcomes, predicted match results and predicted standings
#### 9. data/train_data/final.csv
- csv file used for training a model and making predictions
#### 10. data/statistics/model_confidence.csv
- list of grid searched classifiers and its confidence score



