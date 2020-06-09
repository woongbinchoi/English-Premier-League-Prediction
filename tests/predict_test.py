import pytest
import os
import pandas as pd
import requests
from predict import (
    prepare_data,
)
from constants import (
    FINAL_FILE,
)


def test_prepare_data_difference():
    data = pd.read_csv(FINAL_FILE)
    prepared_data = prepare_data(data)

    data_columns = list(data)
    prepared_columns = list(prepared_data)

    assert 'Date' in data_columns
    assert 'HomeTeam' in data_columns
    assert 'AwayTeam' in data_columns
    assert 'FTHG' in data_columns
    assert 'FTAG' in data_columns
    assert 'HT_goal_for' in data_columns
    assert 'AT_goal_for' in data_columns
    assert 'HT_goal_against' in data_columns
    assert 'AT_goal_against' in data_columns

    assert 'Date' not in prepared_columns
    assert 'HomeTeam' not in prepared_columns
    assert 'AwayTeam' not in prepared_columns
    assert 'FTHG' not in prepared_columns
    assert 'FTAG' not in prepared_columns
    assert 'HT_goal_for' not in prepared_columns
    assert 'AT_goal_for' not in prepared_columns
    assert 'HT_goal_against' not in prepared_columns
    assert 'AT_goal_against' not in prepared_columns


def test_prepare_data_common():
    data = pd.read_csv(FINAL_FILE)
    prepared_data = prepare_data(data)

    data_columns = list(data)
    prepared_columns = list(prepared_data)

    assert 'HT_3_win_streak' in data_columns
    assert 'HT_5_win_streak' in data_columns
    assert 'HT_3_lose_Streak' in data_columns
    assert 'HT_5_lose_Streak' in data_columns
    assert 'AT_3_win_streak' in data_columns
    assert 'AT_5_win_streak' in data_columns
    assert 'AT_3_lose_Streak' in data_columns
    assert 'AT_5_lose_Streak' in data_columns

    assert 'HT_3_win_streak' in prepared_columns
    assert 'HT_5_win_streak' in prepared_columns
    assert 'HT_3_lose_Streak' in prepared_columns
    assert 'HT_5_lose_Streak' in prepared_columns
    assert 'AT_3_win_streak' in prepared_columns
    assert 'AT_5_win_streak' in prepared_columns
    assert 'AT_3_lose_Streak' in prepared_columns
    assert 'AT_5_lose_Streak' in prepared_columns
