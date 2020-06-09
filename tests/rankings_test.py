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
