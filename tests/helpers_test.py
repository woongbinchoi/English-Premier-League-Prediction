import pytest
import os
import pandas as pd
import requests
from helpers import (
    copy_csv,
    compare_csv,
    make_directory,
    remove_directory,
)
from constants import (
    FINAL_FILE,
)

def test_copy_csv():
    temp_folder = os.path.join(os.getcwd(), 'temp')
    temp_file = os.path.join(temp_folder, 'temp.csv')
    remove_directory(temp_folder)

    assert not os.path.isfile(temp_file)
    assert not os.path.isdir(temp_folder)
    
    copy_csv(FINAL_FILE, temp_file)
    
    assert os.path.isfile(temp_file)
    assert os.path.isdir(temp_folder)
    assert compare_csv(FINAL_FILE, temp_file)
    
    remove_directory(temp_folder)


def test_compare_csv():
    temp_folder = os.path.join(os.getcwd(), 'temp')
    temp_file = os.path.join(temp_folder, 'temp.csv')
    remove_directory(temp_folder)

    assert not os.path.isfile(temp_file)
    assert not os.path.isdir(temp_folder)
    
    copy_csv(FINAL_FILE, temp_file)

    assert compare_csv(FINAL_FILE, temp_file)
    assert compare_csv(temp_file, temp_file)
    assert compare_csv(FINAL_FILE, FINAL_FILE)

    remove_directory(temp_folder)

