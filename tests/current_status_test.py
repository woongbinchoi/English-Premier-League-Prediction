import pytest
import os
import requests
from rankings import (
    get_rankings,
    get_rankings_all,
)
from constants import (
    CURRENT_YEAR,
    RAW_CLEANED_DATA_FILE_PATH,
    STANDINGS_PATH,
)
from helpers import (
    make_directory,
    remove_directory,
    compare_csv,
)
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


def test_get_rankings_year_before_sofifa():
    year = 1993
    temp_folder = os.path.join(os.getcwd(), 'temp')
    csv_file = '{}-{}.csv'.format(year, year + 1)
    from_file = os.path.join(RAW_CLEANED_DATA_FILE_PATH, csv_file)
    to_file = os.path.join(temp_folder, csv_file)
    make_directory(to_file)

    get_rankings(from_file, to_file, '{}-12-31'.format(str(year+1)), include_prediction=False)

    cmp_file = os.path.join(STANDINGS_PATH, csv_file)
    assert compare_csv(cmp_file, to_file)
    remove_directory(temp_folder)

def test_get_rankings_year_after_sofifa():
    year = 2008
    temp_folder = os.path.join(os.getcwd(), 'temp')
    csv_file = '{}-{}.csv'.format(year, year + 1)
    from_file = os.path.join(RAW_CLEANED_DATA_FILE_PATH, csv_file)
    to_file = os.path.join(temp_folder, csv_file)
    make_directory(temp_folder)

    get_rankings(from_file, to_file, '{}-12-31'.format(str(year+1)), include_prediction=False)

    cmp_file = os.path.join(STANDINGS_PATH, csv_file)
    assert compare_csv(cmp_file, to_file)
    remove_directory(temp_folder)

def test_get_rankings_all():
    temp_folder = os.path.join(os.getcwd(), 'temp/file.csv')
    make_directory(temp_folder)

    from_year, to_year = 1993, 2019
    get_rankings_all(from_year, to_year, RAW_CLEANED_DATA_FILE_PATH, temp_folder)

    for year in range(from_year, to_year + 1):
        csv_file = '{}-{}.csv'.format(year, year + 1)
        created_file = os.path.join(temp_folder, csv_file)
        cmp_file = os.path.join(STANDINGS_PATH, csv_file)
        assert compare_csv(cmp_file, created_file)
    remove_directory(temp_folder)
