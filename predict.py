import pandas as pd
from IPython import get_ipython
ipy = get_ipython()
if ipy is not None:
    ipy.run_line_magic('matplotlib', 'inline')

from sklearn.preprocessing import scale
from sklearn.cross_validation import train_test_split
from time import time 
from sklearn.metrics import f1_score

import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import SGDClassifier

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from sklearn.grid_search import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import expon

def prepare_data(data):
    ''' Drops unnecessary columns, Fill or Drop rows containing N/A, and pre-processes the columns.'''
    data = data.drop(columns=['Date', 'HomeTeam', 'AwayTeam'])
    data = data.drop(columns=['HT_goal_for', 'AT_goal_for', 'HT_goal_against', 'AT_goal_against'])
    #data = data.drop(columns=['HT_3_win_streak', 'HT_5_win_streak', 'HT_3_lose_Streak', 'HT_5_lose_Streak', 
    #                          'AT_3_win_streak', 'AT_5_win_streak', 'AT_3_lose_Streak', 'AT_5_lose_Streak'])
    
    #data.fillna(value=-99999, inplace=True)
    data = data.dropna()
    
    # Columns that are not normalized: (Ordinal, Categorical)
    # [FTR, HT_match_played, AT_match_played, HT_3_win_streak, HT_5_win_streak, 
    # HT_3_lose_Streak, HT_5_lose_Streak, AT_3_win_streak, AT_5_win_streak, AT_3_lose_Streak, AT_5_lose_Streak]
    
    # Columns that are normalized: (Continuous variables)
    normalizedColumns = ['HomeOVA', 'AwayOVA', 'OVA_diff']
    normalizedColumns += ['HT_current_standing', 'AT_current_standing']
    normalizedColumns += [ 'HT_goal_diff', 'HT_win_rate_season', 'AT_goal_diff', 'AT_win_rate_season']
    normalizedColumns += ['HT_past_standing', 'HT_past_goal_diff', 'HT_past_win_rate',
                          'AT_past_standing', 'AT_past_goal_diff', 'AT_past_win_rate']
    normalizedColumns += ['HT_5_win_rate', 'AT_5_win_rate', 'HT_win_rate_against', 'AT_win_rate_against']
    normalizedColumns += ['current_standing_diff', 'win_rate_season_diff', 'goal_diff_diff']
    normalizedColumns += ['past_standing_diff', 'past_goal_diff_diff', 'past_win_rate_diff']
    #normalizedColumns += ['HT_goal_for', 'AT_goal_for', 'HT_goal_against', 'AT_goal_against']
    
    for column in normalizedColumns:
        data[column] = scale(data[column])
    
    return data
    

def train_classifier(clf, X_train, y_train):
    ''' Fits a classifier to the training data. '''
    
    # Start the clock, train the classifier, then stop the clock
    start = time()
    clf.fit(X_train, y_train)
    end = time()
    
    # Print the results
#    print("Trained model in {:.4f} seconds".format(end - start))

    
def predict_labels(clf, features, target):
    ''' Makes predictions using a fit classifier based on F1 score. '''
    
    # Start the clock, make predictions, then stop the clock
    start = time()
    y_pred = clf.predict(features)
    end = time()
    # Print and return results
#    print("Made predictions in {:.4f} seconds.".format(end - start))
    
    return f1_score(target, y_pred, labels=['H','D','A'], average = None), sum(target == y_pred) / float(len(y_pred)), clf.score(features, target)


def train_predict(clf, X_train, y_train, X_test, y_test):
    ''' Train and predict using a classifer based on F1 score. '''
    
    # Indicate the classifier and the training set size
    print("Training a {} using a training set size of {}. . .".format(clf.__class__.__name__, len(X_train)))
    
    # Train the classifier
    train_classifier(clf, X_train, y_train)
    
    # Print the results of prediction for both training and testing
    f1, acc, confidence = predict_labels(clf, X_train, y_train)
#    print(f1, acc)
#    print("F1 score and accuracy score for training set: {} , {}.".format(f1 , acc))
#    print("Confidence score for training set: {}.".format(confidence))
    
    f1, acc, confidence = predict_labels(clf, X_test, y_test)
#    print("F1 score and accuracy score for test set: {} , {}.".format(f1 , acc))
    print("Confidence score for test set: {}.".format(confidence))
    print()
    

def train_predict_grid(clf, scoring, param, X_all, y_all, X_train, y_train, X_test, y_test):
    gridsearch = GridSearchCV(clf, 
                              scoring=scoring, 
                              param_grid=param)
    grid_obj = gridsearch.fit(X_all,y_all)
    
    clf = grid_obj.best_estimator_
    params = grid_obj.best_params_
    print(clf)
    print(params)
    
    train_predict(clf, X_train, y_train, X_test, y_test)


def train_predict_random(clf, scoring, param, X_all, y_all, X_train, y_train, X_test, y_test):
    randomsearch = RandomizedSearchCV(clf, param, 
                                      n_iter=10, 
                                      scoring=scoring)
    random_obj = randomsearch.fit(X_all,y_all)
    
    clf = random_obj.best_estimator_
    params = random_obj.best_params_
    print(clf)
    print(params)
    
    train_predict(clf, X_train, y_train, X_test, y_test)
    
    

data = pd.read_csv('data/final.csv')
data = prepare_data(data)

X_all = data.drop(columns=['FTR'])
y_all = data['FTR']

X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, test_size = 0.3)

clf_A = LogisticRegression()
clf_B = SVC(kernel='rbf')
clf_C = xgb.XGBClassifier()
clf_D = KNeighborsClassifier()
clf_E = RandomForestClassifier()
clf_F = GaussianNB()
clf_G = DecisionTreeClassifier()
clf_H = GradientBoostingClassifier()
clf_I = LinearSVC()
clf_J = SGDClassifier()

clf_K = xgb.XGBClassifier()
parameters_K = { 'learning_rate' : [0.1],
               'n_estimators' : [40],
               'max_depth': [3],
               'min_child_weight': [3],
               'gamma':[0.4],
               'subsample' : [0.8],
               'colsample_bytree' : [0.8],
               'scale_pos_weight' : [1],
               'reg_alpha':[1e-5]
             }  
f1_scorer_K = make_scorer(f1_score, labels=['H','D','A'], average = 'micro')

clf_L = LogisticRegression()
C_distr = expon(scale=2)
parameters_L = {'C': C_distr, 'penalty': ['l1', 'l2']}
f1_scorer_L = make_scorer(f1_score, labels=['H','D','A'], average = 'micro')


#train_predict(clf_A, X_train, y_train, X_test, y_test)
#train_predict(clf_B, X_train, y_train, X_test, y_test)
#train_predict(clf_C, X_train, y_train, X_test, y_test)
#train_predict(clf_D, X_train, y_train, X_test, y_test)
#train_predict(clf_E, X_train, y_train, X_test, y_test)
#train_predict(clf_F, X_train, y_train, X_test, y_test)
#train_predict(clf_G, X_train, y_train, X_test, y_test)
#train_predict(clf_H, X_train, y_train, X_test, y_test)
#train_predict(clf_I, X_train, y_train, X_test, y_test)
#train_predict(clf_J, X_train, y_train, X_test, y_test)
#train_predict_grid(clf_K, f1_scorer_K, parameters_K, X_all, y_all, X_train, y_train, X_test, y_test)
train_predict_random(clf_L, f1_scorer_L, parameters_L, X_all, y_all, X_train, y_train, X_test, y_test)



