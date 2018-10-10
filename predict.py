#data preprocessing
import pandas as pd
#produces a prediction model in the form of an ensemble of weak prediction models, typically decision tree
import xgboost as xgb
#the outcome (dependent variable) has only a limited number of possible values. 
#Logistic Regression is used when response variable is categorical in nature.
from sklearn.linear_model import LogisticRegression
#A random forest is a meta estimator that fits a number of decision tree classifiers 
#on various sub-samples of the dataset and use averaging to improve the predictive 
#accuracy and control over-fitting.
from sklearn.ensemble import RandomForestClassifier
#a discriminative classifier formally defined by a separating hyperplane.
from sklearn.svm import SVC

from sklearn.svm import LinearSVC
#displayd data
#from IPython.display import display
from IPython import get_ipython
ipy = get_ipython()
if ipy is not None:
    ipy.run_line_magic('matplotlib', 'inline')
    
# Standardising the data.
from sklearn.preprocessing import scale

from sklearn.cross_validation import train_test_split

#for measuring training time
from time import time 
# F1 score (also F-score or F-measure) is a measure of a test's accuracy. 
#It considers both the precision p and the recall r of the test to compute 
#the score: p is the number of correct positive results divided by the number of 
#all positive results, and r is the number of correct positive results divided by 
#the number of positive results that should have been returned. The F1 score can be 
#interpreted as a weighted average of the precision and recall, where an F1 score 
#reaches its best value at 1 and worst at 0.
from sklearn.metrics import f1_score

from sklearn.neighbors import KNeighborsClassifier

from sklearn.naive_bayes import GaussianNB

from sklearn.tree import DecisionTreeClassifier

from sklearn.ensemble import GradientBoostingClassifier

from sklearn.linear_model import SGDClassifier


import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

data = pd.read_csv('data/final.csv')
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



X_all = data.drop(columns=['FTR'])
y_all = data['FTR']
# Shuffle and split the dataset into training and testing set.
X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, test_size = 0.3)


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
    
# Initialize the three models (XGBoost is initialized later)
clf_A = LogisticRegression()
clf_B = SVC(kernel='rbf')
#Boosting refers to this general problem of producing a very accurate prediction rule 
#by combining rough and moderately inaccurate rules-of-thumb
clf_C = xgb.XGBClassifier()

clf_D = KNeighborsClassifier()

clf_E = RandomForestClassifier()

clf_F = GaussianNB()

clf_G = DecisionTreeClassifier()

clf_H = GradientBoostingClassifier()

clf_I = LinearSVC()

clf_J = SGDClassifier()

train_predict(clf_A, X_train, y_train, X_test, y_test)
print()
train_predict(clf_B, X_train, y_train, X_test, y_test)
print()
train_predict(clf_C, X_train, y_train, X_test, y_test)
print()
train_predict(clf_D, X_train, y_train, X_test, y_test)
print()
train_predict(clf_E, X_train, y_train, X_test, y_test)
print()
train_predict(clf_F, X_train, y_train, X_test, y_test)
print()
train_predict(clf_G, X_train, y_train, X_test, y_test)
print()
train_predict(clf_H, X_train, y_train, X_test, y_test)
print()
train_predict(clf_I, X_train, y_train, X_test, y_test)
print()
train_predict(clf_J, X_train, y_train, X_test, y_test)
print()







# TODO: Import 'GridSearchCV' and 'make_scorer'
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import make_scorer


# TODO: Create the parameters list you wish to tune
parameters = { 'learning_rate' : [0.1],
               'n_estimators' : [40],
               'max_depth': [3],
               'min_child_weight': [3],
               'gamma':[0.4],
               'subsample' : [0.8],
               'colsample_bytree' : [0.8],
               'scale_pos_weight' : [1],
               'reg_alpha':[1e-5]
             }  

# TODO: Initialize the classifier
clf = xgb.XGBClassifier()

# TODO: Make an f1 scoring function using 'make_scorer' 
f1_scorer = make_scorer(f1_score, labels=['H','D','A'], average = 'micro')

# TODO: Perform grid search on the classifier using the f1_scorer as the scoring method
grid_obj = GridSearchCV(clf,
                        scoring=f1_scorer,
                        param_grid=parameters)

# TODO: Fit the grid search object to the training data and find the optimal parameters
grid_obj = grid_obj.fit(X_train,y_train)

# Get the estimator
clf = grid_obj.best_estimator_
print(clf)

# Report the final F1 score for training and testing after parameter tuning
#f1, acc, confidence = predict_labels(clf, X_train, y_train)
#print( "F1 score and accuracy score for training set: {} , {}.".format(f1 , acc))
#print("Confidence score for training set: {}.".format(confidence))
    
f1, acc, confidence = predict_labels(clf, X_test, y_test)
#print( "F1 score and accuracy score for test set: {} , {}.".format(f1 , acc))
print("Confidence score for test set: {}.".format(confidence))






from sklearn.model_selection import RandomizedSearchCV

from scipy.stats import expon

clf = LogisticRegression()
C_distr = expon(scale=2)
param_grid_random = {'C': C_distr, 'penalty': ['l1', 'l2']}
randomsearch = RandomizedSearchCV(clf, param_grid_random, n_iter=10)

# TODO: Fit the grid search object to the training data and find the optimal parameters
grid_obj = randomsearch.fit(X_all,y_all)

# Get the estimator
clf = grid_obj.best_estimator_
print(clf)

params = grid_obj.best_params_
print(params)

# Report the final F1 score for training and testing after parameter tuning
#f1, acc, confidence = predict_labels(clf, X_train, y_train)
#print( "F1 score and accuracy score for training set: {} , {}.".format(f1 , acc))
#print("Confidence score for training set: {}.".format(confidence))
    
f1, acc, confidence = predict_labels(clf, X_test, y_test)
#print( "F1 score and accuracy score for test set: {} , {}.".format(f1 , acc))
print("Confidence score for test set: {}.".format(confidence))

clf = LogisticRegression(C=params['C'], penalty=params['penalty'])
train_predict(clf, X_train, y_train, X_test, y_test)
print()

