import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# Constants
timeout = 5
sleepTime = 0.5
NameChangeMap = {
	'Birmingham': 'Birmingham City',
	'Blackburn': 'Blackburn Rovers',
	'Bolton': 'Bolton Wanderers',
	'Brighton': 'Brighton & Hove Albion',
	'Cardiff': 'Cardiff City',
	'Charlton': 'Charlton Athletic',
	'Derby': 'Derby County',
	'Huddersfield': 'Huddersfield Town',
	'Hull': 'Hull City',
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

# Scrape EPL team OVA data from sofifa.com from {fromYear} to {toYear} season and save the collected data in {csvPath}
def scrapeTeamOVA(fromYear, toYear, csvPath):
	if not os.path.exists(csvPath):
		os.makedirs(csvPath)

	# Start scraping.
	browser = webdriver.Chrome()
	browser.get("https://sofifa.com/teams/hot")

	try:
	    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='choose-version']")))
	except TimeoutException:
	    print("Timed out waiting for page to load")
	    browser.quit()

	# Clicks
	for year in range(fromYear, toYear + 1):
		fifaVersion = str(format((year % 2000 + 1), '02d'))

		ShowListButton = browser.find_element_by_xpath("//a[@class='choose-version']")
		ShowListButton.click()
		time.sleep(sleepTime * 2)

		FifaYearButton = browser.find_element_by_xpath("//label[contains(text(), 'FIFA " + fifaVersion + "')]")
		FifaYearButton.click()
		time.sleep(sleepTime * 2)

		LatestDataButton = browser.find_element_by_xpath("//div[@data-tag='tag-fifa-" + fifaVersion + "']//a[@rel='nofollow']")
		LatestDataButton.click()
		time.sleep(sleepTime * 2)

		LeagueInputBox = browser.find_element_by_xpath("//div[@class='form-autocomplete-input form-input']//input[@placeholder='Leagues']")
		LeagueInputBox.click()
		time.sleep(sleepTime)
		LeagueInputBox.send_keys('English Premier League')
		time.sleep(sleepTime)
		LeagueInputBox.send_keys(Keys.RETURN)
		time.sleep(sleepTime)
		LeagueInputBox.submit()
		time.sleep(sleepTime * 2)

		# Collect the data we need
		NameElements = browser.find_elements_by_xpath("//tbody/tr/td[2]/div/a")
		OVAElements = browser.find_elements_by_xpath("//tbody/tr/td[4]/div/span")
		titles = [x.text for x in NameElements]
		OVAs = [x.text for x in OVAElements]

		# Print the data we have
		print()
		print("Data for ", year)
		print("Titles    |     OVA")
		for title, OVA in zip(titles, OVAs):
			print(title, "   ", OVA)

		# Data to csv
		df = pd.DataFrame.from_records(zip(titles, OVAs), columns=["Team", "OVA"])
		df.set_index('Team', inplace=True)
		filePath = "{}/{}-{}.csv".format(csvPath, year, year + 1)
		df.to_csv(filePath)

def convertTeamName(name):
	return NameChangeMap[name] if name in NameChangeMap else name

def mergeOVAToCleaned(ovaPath, cleanedPath):
	OVAdf = pd.read_csv(ovaPath)
	cleaneddf = pd.read_csv(cleanedPath)

	OVAdf.set_index('Team', inplace=True)

	HomeOVAs, AwayOVAs = [], []
	for index, row in cleaneddf.iterrows():
		HT = convertTeamName(row['HomeTeam'])
		AT = convertTeamName(row['AwayTeam'])
		HomeOVAs.append(OVAdf.loc[HT]['OVA'])
		AwayOVAs.append(OVAdf.loc[AT]['OVA'])

	cleaneddf['HomeOVA'] = pd.Series(HomeOVAs, index=cleaneddf.index)
	cleaneddf['AwayOVA'] = pd.Series(AwayOVAs, index=cleaneddf.index)
	cleaneddf['OVA_diff'] = cleaneddf['HomeOVA'] - cleaneddf['AwayOVA']
	cleaneddf.to_csv(cleanedPath, index=False)

def scrapeTeamOVAAll(path, fromYear, toYear):
	scrapeTeamOVA(fromYear, toYear, path)

def mergeOVAToCleanedAll(ovaFolderPath, cleanedFolderPath, fromYear, toYear):
	for year in range(fromYear, toYear + 1):
		ovaPath = os.path.join(ovaFolderPath, '{}-{}.csv'.format(year, year + 1))
		cleanedPath = os.path.join(cleanedFolderPath, '{}-{}.csv'.format(year, year + 1))

		print("About to merge " + ovaPath + " ...")
		mergeOVAToCleaned(ovaPath, cleanedPath)
