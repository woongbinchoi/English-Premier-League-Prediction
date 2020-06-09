import pytest
import os
import pandas as pd
import requests
from match_history import (
    get_current_fixtures,
    convert_team_name,
)
from helpers import (
    make_directory,
    remove_directory,
)

def test_get_current_fixtures_api():
    base_url = "http://api.football-data.org/v2/competitions/"
    AUTH_TOKEN = "9f2efd00a5604f59a8f1c54860786e31"
    headers={"X-Auth-Token": AUTH_TOKEN}
    
    england_area_code = 2072
    list_competitions_url = base_url + "?areas=" + str(england_area_code)
    req = requests.get(list_competitions_url, headers=headers)
    assert req.status_code == 200


def test_convert_team_name_exists():
    assert convert_team_name('Manchester United FC') == 'Man United'
    assert convert_team_name('Leicester City FC') == 'Leicester'
    assert convert_team_name('Tottenham Hotspur FC') == 'Tottenham'
    assert convert_team_name('Newcastle United FC') == 'Newcastle'
    assert convert_team_name('Chelsea FC') == 'Chelsea'
    assert convert_team_name('Huddersfield Town AFC') == 'Huddersfield'


def test_convert_team_name_not_exists():
    assert convert_team_name('Chelsea') == 'Chelsea'
    assert convert_team_name('Liverpool') == 'Liverpool'
    assert convert_team_name('Derby') == 'Derby'
    assert convert_team_name('Brighton') == 'Brighton'
    assert convert_team_name('Southampton') == 'Southampton'
    assert convert_team_name('Sheffield') == 'Sheffield'


def test_get_current_fixtures():
    temp_folder = os.path.join(os.getcwd(), 'temp')
    temp_file = os.path.join(temp_folder, 'temp.csv')
    make_directory(temp_file)
    get_current_fixtures(temp_file)

    assert os.path.isfile(temp_file)
    df = pd.read_csv(temp_file)
    df_columns_list = list(df)

    assert 'Date' in df_columns_list
    assert 'HomeTeam' in df_columns_list
    assert 'AwayTeam' in df_columns_list
    assert 'FTHG' in df_columns_list
    assert 'FTAG' in df_columns_list
    assert 'FTR' in df_columns_list

    remove_directory(temp_folder)