import pytest
import requests
from sofifa_scraper import (
    convert_team_name,
)

def test_scrape_team_ova():
    r = requests.get("https://sofifa.com/teams?type=all&lg%5B%5D=13")
    assert r.status_code == 200

def test_convert_team_name_exists():
    assert convert_team_name('Birmingham') == 'Birmingham City'
    assert convert_team_name('Bolton') == 'Bolton Wanderers'
    assert convert_team_name('Wigan') == 'Wigan Athletic'

def test_convert_team_name_not_exists():
    assert convert_team_name('Chelsea') == 'Chelsea'
    assert convert_team_name('Liverpool') == 'Liverpool'
    assert convert_team_name('Derby') != 'Derby'
