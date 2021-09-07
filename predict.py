import os.path
import json
import joblib
import pandas as pd
import numpy as np
from IPython import get_ipython
ipy = get_ipython()
if ipy is not None:
    ipy.run_line_magic('matplotlib', 'inline')

from sklearn.preprocessing import scale
from sklearn.model_selection import KFold
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
warnings.filterwarnings("ignore", category=FutureWarning)

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import expon

from helpers import make_directory


def prepare_data(data, drop_na=True):
    ''' Drops unnecessary columns, Fill or Drop rows containing N/A, and pre-processes the columns.'''
    data = data.drop(columns=['Date', 'HomeTeam', 'AwayTeam'])
    data = data.drop(columns=['FTHG','FTAG'])
    data = data.drop(columns=['HT_goal_for', 'AT_goal_for', 'HT_goal_against', 'AT_goal_against'])
    #data = data.drop(columns=['HT_3_win_streak', 'HT_5_win_streak', 'HT_3_lose_Streak', 'HT_5_lose_Streak', 
    #                          'AT_3_win_streak', 'AT_5_win_streak', 'AT_3_lose_Streak', 'AT_5_lose_Streak'])
    
    data = data.loc[data['HT_match_played'] == data['HT_match_played']]
    
    if drop_na:
        data = data.dropna()
    else:
        data.fillna(value=-99999, inplace=True)
    
    # Columns that are not normalized: (Ordinal, Categorical)
    # [FTR, HT_match_played, AT_match_played, HT_3_win_streak, HT_5_win_streak, 
    # HT_3_lose_Streak, HT_5_lose_Streak, AT_3_win_streak, AT_5_win_streak, AT_3_lose_Streak, AT_5_lose_Streak]
    
    # Columns that are normalized: (Continuous variables)
    normalized_columns = ['HomeOVA', 'AwayOVA', 'OVA_diff']
    normalized_columns += ['HT_current_standing', 'AT_current_standing']
    normalized_columns += [ 'HT_goal_diff', 'HT_win_rate_season', 'AT_goal_diff', 'AT_win_rate_season']
    normalized_columns += ['HT_past_standing', 'HT_past_goal_diff', 'HT_past_win_rate',
                          'AT_past_standing', 'AT_past_goal_diff', 'AT_past_win_rate']
    normalized_columns += ['HT_5_win_rate', 'AT_5_win_rate', 'HT_win_rate_against', 'AT_win_rate_against']
    normalized_columns += ['current_standing_diff', 'win_rate_season_diff', 'goal_diff_diff']
    normalized_columns += ['past_standing_diff', 'past_goal_diff_diff', 'past_win_rate_diff']
    #normalized_columns += ['HT_goal_for', 'AT_goal_for', 'HT_goal_against', 'AT_goal_against']

    for column in normalized_columns:
        data[column] = scale(list(data[column]))
    return data


def train_classifier(clf, X_train, y_train):
    ''' Fits a classifier to the training data. '''
    
    # Start the clock, train the classifier, then stop the clock
    start = time()
    clf.fit(X_train, y_train)
    end = time()
    
    # Print the results
    # print("Trained model in {:.4f} seconds".format(end - start))

    
def predict_labels(clf, features, target):
    ''' Makes predictions using a fit classifier based on F1 score. '''
    
    # Start the clock, make predictions, then stop the clock
    start = time()
    y_pred = clf.predict(features)
    end = time()
    # Print and return results
    # print("Made predictions in {:.4f} seconds.".format(end - start))
    return f1_score(target, y_pred, labels=['H','D','A'], average = None), sum(target == y_pred) / float(len(y_pred)), clf.score(features, target), y_pred


def train_predict(clf, X_train, y_train, X_test, y_test):
    ''' Train and predict using a classifer based on F1 score. '''
    
    # Indicate the classifier and the training set size
    print("Training a {} using a training set size of {}. . .".format(clf.__class__.__name__, len(X_train)))
    
    # Train the classifier
    train_classifier(clf, X_train, y_train)
    
    # Print the results of prediction for both training and testing
    f1, acc, confidence, _ = predict_labels(clf, X_train, y_train)
    # print("F1 score and accuracy score for training set: {} , {}.".format(f1 , acc))
    # print("Confidence score for training set: {}.".format(confidence))
    
    f1, acc, confidence, predictions = predict_labels(clf, X_test, y_test)
    # print("F1 score and accuracy score for test set: {} , {}.".format(f1 , acc))
    print("Confidence score for test set: {}.".format(confidence))
    print()
    
    return confidence, predictions


def get_grid_clf(clf, scoring, param, X_all, y_all):
    gridsearch = GridSearchCV(clf, 
                              scoring=scoring, 
                              param_grid=param, 
                              verbose=100)
    grid_obj = gridsearch.fit(X_all,y_all)

    clf = grid_obj.best_estimator_
    params = grid_obj.best_params_
    print(clf)
    print(params)

    return clf


def get_random_clf(clf, scoring, param, X_all, y_all):
    randomsearch = RandomizedSearchCV(clf, param, 
                                      n_iter=10,
                                      scoring=scoring,
                                      verbose=100)
    random_obj = randomsearch.fit(X_all,y_all)
    
    clf = random_obj.best_estimator_
    params = random_obj.best_params_
    print(clf)
    print(params)
    return clf


def process_print_result(clfs, res):
    def average(lst):
        return sum(lst) / len(lst)
    
    avg_dict = {}
    best_clf_so_far = 0
    best_avg_so_far = -1
    for i in range(len(clfs)):
        clf_name = clfs[i].__class__.__name__
        if clf_name in avg_dict:
            clf_name += json.dumps(clfs[i].get_params())
        avg = average(res[i])
        avg_dict[clf_name] = avg
        if avg > best_avg_so_far:
        	best_avg_so_far = avg
        	best_clf_so_far = i
    
    for clf_name in sorted(avg_dict, key=avg_dict.get, reverse=True):
        print("{}: {}".format(clf_name, avg_dict[clf_name]))
    
    return avg_dict, clfs[best_clf_so_far], best_avg_so_far


def get_clf(final_file_path, model_confidence_csv_path, clf_file, recalculate=True):
    if not recalculate and os.path.isfile(clf_file):
        return joblib.load(clf_file), None, None
        
    # First load the data from csv file
    data = pd.read_csv(final_file_path)
    
    # Drop columns that are not needed and normalized each columns
    data = prepare_data(data, drop_na=True)
    data = data.loc[(data['FTR'] == 'H') | (data['FTR'] == 'D') | (data['FTR'] == 'A')]
    
    # Divide data into features and label
    X_all = data.drop(columns=['FTR'])
    y_all = data['FTR']

    # List of Classifiers that we are going to run
    classifiers = [
        # Logistic Regressions
        LogisticRegression(),
        # Best param in this grid search
        LogisticRegression(penalty='l2', solver='newton-cg', multi_class='ovr',
                            C=0.1, warm_start=True),
        LogisticRegression(penalty='l2', solver='lbfgs', multi_class='multinomial',
                            C=0.4, warm_start=False),
        # SVC
        SVC(probability=True),
        SVC(C=0.3, class_weight=None, decision_function_shape='ovo', degree=1,
            kernel='rbf', probability=True, shrinking=True, tol=0.0005),
        SVC(C=0.28, class_weight=None, decision_function_shape='ovo', degree=1,
            kernel='rbf', probability=True, shrinking=True, tol=0.0002),
        # XGBoost
        xgb.XGBClassifier(),
        xgb.XGBClassifier(learning_rate=0.01, n_estimators=1000, max_depth=2,
            min_child_weight=5, gamma=0, subsample=0.8, colsample_bytree=0.7,
            scale_pos_weight=0.8, reg_alpha=1e-5, booster='gbtree', objective='multi:softprob'),
        # KNeighborsClassifier(),
        # RandomForestClassifier(),
        # GaussianNB(),
        # DecisionTreeClassifier(),
        # GradientBoostingClassifier(),
        # LinearSVC(),
        # SGDClassifier()
    ]
    
    # # Example of how to grid search classifiers
    # # Logistic Regression
    # clf_L = LogisticRegression()
    # parameters_L = {'penalty': ['l2'], 
    #                 'solver': ['lbfgs', 'newton-cg', 'sag'], 
    #                 'multi_class': ['ovr', 'multinomial'],
    #                 'C': [x * 0.1 + 0.1 for x in range(10)],
    #                 'warm_start': [True, False],
    #                 'fit_intercept':[True, False],
    #                 'class_weight':['balanced',None]}
    # f1_scorer_L = make_scorer(f1_score, labels=['H','D','A'], average = 'micro')
    # clf_L = get_grid_clf(clf_L, f1_scorer_L, parameters_L, X_all, y_all)
    # classifiers.append(clf_L)
    
    # # SVC
    # clf_L = SVC()
    # parameters_L = {
    #         'C': [x * 0.01 + 0.27 for x in range(5)], 
    #         'kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
    #         'degree': [x + 1 for x in range(3)],
    #         'shrinking': [True, False],
    #         'tol':[x * 0.0005 + 0.0005 for x in range(3)],
    #         'class_weight':['balanced',None],
    #         'decision_function_shape': ['ovo', 'ovr']
    #         }
    # f1_scorer_L = make_scorer(f1_score, labels=['H','D','A'], average = 'micro')
    # clf_L = get_grid_clf(clf_L, f1_scorer_L, parameters_L, X_all, y_all)
    # classifiers.append(clf_L)
    
    # # XGBoost
    # clf_L = xgb.XGBClassifier()
    # parameters_L = {
    #         'learning_rate': [0.01],
    #         'n_estimators':[1000],
    #         'max_depth': [2],
    #         'min_child_weight': [5],
    #         'gamma': [0],
    #         'subsample': [0.8],
    #         'colsample_bytree': [0.7],
    #         'scale_pos_weight':[0.8],
    #         'reg_alpha':[1e-5],
    #         'booster': ['gbtree'],
    #         'objective': ['multi:softprob']
    #         }
    # f1_scorer_L = make_scorer(f1_score, labels=['H','D','A'], average = 'micro')
    # clf_L = get_grid_clf(clf_L, f1_scorer_L, parameters_L, X_all, y_all)
    # classifiers.append(clf_L)

    # We are going to record accuracies of each classifier prediction iteration
    len_classifiers = len(classifiers)
    result = [[] for _ in range(len_classifiers)]
    y_results = [[] for _ in range(len_classifiers + 1)]

    # Using 10-fold cross validation (Dividing the data into sub groups (90% to fit, 10% to test), and run 
    # prediction with each classifiers using the sub groups as a dataset)
    split = 10
    kf = KFold(n_splits=split, shuffle=True)
    for split_index, (train_index, test_index) in enumerate(kf.split(X_all)):
        print("Processing {}/{} of KFold Cross Validation...".format(split_index + 1, split))
        X_train, X_test = X_all.iloc[train_index], X_all.iloc[test_index]
        y_train, y_test = y_all.iloc[train_index], y_all.iloc[test_index]
        y_results[len_classifiers] += y_test.tolist()
        
        for index, clf in enumerate(classifiers):
            print("KFold: {}/{}. clf_index: {}/{}.".format(split_index + 1, split, index + 1, len(classifiers)))
            confidence, predicted_result = train_predict(clf, X_train, y_train, X_test, y_test)
            result[index].append(confidence)
            y_results[index] += predicted_result.tolist()

    # Make a dictionary of average accuracies for each classifiers
    avg_dict, best_clf, best_clf_average = process_print_result(classifiers, result)

    # Put the result into csv file
    if os.path.isfile(model_confidence_csv_path):    
        df = pd.read_csv(model_confidence_csv_path)
        newdf = pd.DataFrame(avg_dict, index=[df.shape[1]])
        df = pd.concat([df, newdf], ignore_index=True, sort=False)
    else:
        make_directory(model_confidence_csv_path)
        df = pd.DataFrame(avg_dict, index=[0])
    df.to_csv(model_confidence_csv_path, index=False)

    # Saves the classifier using joblib module
    joblib.dump(best_clf, clf_file)

    # Return the best classifier
    return best_clf, y_results, best_clf_average


def predict_next_round(clf, final_path, current_raw_cleaned_path, statistics=False, stat_path=None, first=True):
    # First indicates whether the one being predicted is the upcoming round

    # Load final data csv
    df = pd.read_csv(final_path)
    
    # Get the row count of the dataframe
    len_df = df.shape[0]
    
    # Normalize each columns and remove rows that should not be predicted yet
    df = prepare_data(df, drop_na=False)
    df = df.loc[(df['FTR'] != 'H') & (df['FTR'] != 'D') & (df['FTR'] != 'A')]
    df = df.drop(columns=['FTR'])
    
    if statistics:
        if stat_path is not None:
            make_directory(stat_path)
        else:
            raise ValueError("specify 'stat_path' to save prediction result. Exiting...")
    
    if len(df) > 0:
        df_indices = [x - len_df for x in df.index]
        
        prediction = clf.predict(df).tolist()
        prediction_probability = clf.predict_proba(df).tolist()
        clf_classes = clf.classes_
        
        df_to_predict = pd.read_csv(current_raw_cleaned_path)
        len_df = df_to_predict.shape[0]
        
        print("{:20} {:20} {:20} {}".format("Home", "Away", "Predict", "Probability"))
        for (index, result, pred_prob) in zip(df_indices, prediction, prediction_probability):
            HT = df_to_predict.at[index + len_df, 'HomeTeam']
            AT = df_to_predict.at[index + len_df, 'AwayTeam']
            date_so_far = df_to_predict.at[index + len_df, 'Date']
            
            df_to_predict.at[index + len_df, 'FTR'] = result
            df_to_predict.at[index + len_df, 'FTHG'] = 0
            df_to_predict.at[index + len_df, 'FTAG'] = 0
            
            for (outcome, prob) in zip(clf_classes, pred_prob):
                df_to_predict.at[index + len_df, 'prob_' + outcome] = prob
            
            print("{:20} {:20} {:20} {}".format(HT, AT, HT if result == "H" else AT, max(pred_prob)))
        
        if statistics:
            if first:
                if os.path.exists(stat_path):
                    os.remove(stat_path)
                df_to_predict.to_csv(stat_path, index=False)
            else:
                if os.path.isfile(stat_path):
                    stat_df = pd.read_csv(stat_path)
                    stat_df.update(df_to_predict)
                    stat_df.to_csv(stat_path, index=False)
                else:
                    raise ValueError('FATAL ERROR: either set first=True, or feed stat_path.')

        df_to_predict = df_to_predict.drop(columns=['prob_' + outcome for outcome in clf_classes])
        df_to_predict.to_csv(current_raw_cleaned_path, index=False)
        return True, date_so_far
    else:
        print("There are no more games to make prediction")
        return False, None
