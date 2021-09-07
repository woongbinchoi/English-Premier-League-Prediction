import os
import pandas as pd
from constants import SCRAPER_TIMEOUT, SCRAPER_SLEEP
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time


# Scrape EPL team OVA data from sofifa.com from {from_year} to {to_year} season and save the collected data in {csv_path}
def scrape_team_ova(from_year, to_year, csv_path):
    if not os.path.exists(csv_path):
        os.makedirs(csv_path)

    # Start scraping.
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get("https://sofifa.com/teams?type=all&lg%5B%5D=13&lg%5B%5D=14")

    try:
        WebDriverWait(browser, SCRAPER_TIMEOUT).until(EC.visibility_of_element_located((By.XPATH, "//a[contains(@class, 'bp3-button bp3-minimal text dropdown-toggle')]")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()

    # Clicks
    for year in range(from_year, to_year + 1):
        try:
            filePath = "{}/{}-{}.csv".format(csv_path, year, year + 1)
            if os.path.exists(filePath) and year < to_year - 1:
                # Skip if file already exists and does not need to be updated
                continue
            fifa_version = str(format((year % 2000 + 1), '02d'))

            show_list_button = browser.find_element_by_xpath("//a[contains(@class, 'bp3-button bp3-minimal text dropdown-toggle')]")
            show_list_button.click()
            time.sleep(SCRAPER_SLEEP)

            fifa_year_button = browser.find_element_by_xpath("//a[contains(text(), 'FIFA " + fifa_version + "')]")
            fifa_year_button.click()
            time.sleep(SCRAPER_SLEEP)

            # Collect the data we need
            name_elements = browser.find_elements_by_xpath("//tbody/tr/td[2]/a/div")
            ova_elements = browser.find_elements_by_xpath("//tbody/tr/td[3]/span")
            titles = [x.text for x in name_elements[::2]]
            ovas = [x.text for x in ova_elements]

            # Print the data we have
            print()
            print("Data for ", year)
            print("Titles    |     OVA")
            for title, OVA in zip(titles, ovas):
                print(title, "   ", OVA)

            # Data to csv
            df = pd.DataFrame.from_records(zip(titles, ovas), columns=["Team", "OVA"])
            df.set_index('Team', inplace=True)
            df.to_csv(filePath)
            print(f'Scraping OVA for year {year} completed')
        except Exception as e:
            print(f'Failed to scrape OVA for year {year}')
            print(e)


def convert_team_name(name):
    name_change_map = {
        'Birmingham': 'Birmingham City',
        'Blackburn': 'Blackburn Rovers',
        'Bolton': 'Bolton Wanderers',
        'Brighton': 'Brighton & Hove Albion',
        'Cardiff': 'Cardiff City',
        'Charlton': 'Charlton Athletic',
        'Derby': 'Derby County',
        'Huddersfield': 'Huddersfield Town',
        'Hull': 'Hull City',
        'Leeds': 'Leeds United',
        'Leicester': 'Leicester City',
        'Man City': 'Manchester City',
        'Man United': 'Manchester United',
        'Newcastle': 'Newcastle United',
        'Norwich': 'Norwich City',
        'QPR': 'Queens Park Rangers',
        'Stoke': 'Stoke City',
        'Swansea': 'Swansea City',
        'Tottenham': 'Tottenham Hotspur',
        'West Brom': 'West Bromwich Albion',
        'West Ham': 'West Ham United',
        'Wigan': 'Wigan Athletic',
        'Wolves': 'Wolverhampton Wanderers'
    }
    return name_change_map[name] if name in name_change_map else name


def merge_ova_to_cleaned(ova_path, cleaned_path):
    ova_df = pd.read_csv(ova_path)
    cleaned_df = pd.read_csv(cleaned_path)

    ova_df.set_index('Team', inplace=True)

    home_ovas, away_ovas = [], []
    for _, row in cleaned_df.iterrows():
        HT = convert_team_name(row['HomeTeam'])
        AT = convert_team_name(row['AwayTeam'])
        home_ovas.append(ova_df.loc[HT]['OVA'])
        away_ovas.append(ova_df.loc[AT]['OVA'])

    cleaned_df['HomeOVA'] = pd.Series(home_ovas, index=cleaned_df.index)
    cleaned_df['AwayOVA'] = pd.Series(away_ovas, index=cleaned_df.index)
    cleaned_df['OVA_diff'] = cleaned_df['HomeOVA'] - cleaned_df['AwayOVA']
    cleaned_df.to_csv(cleaned_path, index=False)


def scrape_team_ova_all(path, from_year, to_year):
    scrape_team_ova(from_year, to_year, path)


def merge_ova_to_cleaned_all(ova_folder_path, cleaned_folder_path, from_year, to_year):
    for year in range(from_year, to_year + 1):
        ova_path = os.path.join(ova_folder_path, '{}-{}.csv'.format(year, year + 1))
        if not os.path.exists(ova_path):
            print(f'Using ovapath {ova_path} for year {year} because ova data does not exist...')
            ova_path = os.path.join(ova_folder_path, '{}-{}.csv'.format(year - 1, year))
        cleaned_path = os.path.join(cleaned_folder_path, '{}-{}.csv'.format(year, year + 1))

        print("About to merge " + ova_path + " ...")
        merge_ova_to_cleaned(ova_path, cleaned_path)


if __name__ == "__main__":
    scrape_team_ova_all("data/OVAs", 2006, 2019)