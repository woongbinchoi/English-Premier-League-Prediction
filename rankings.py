
import ntpath
import os
import pandas as pd
import math
from datetime import datetime
import csv

def getRankings(year, date):
	df = pd.read_csv('data/cleaned/%s-%s.csv' % (year, year + 1))
	datet = datetime.strptime(date, '%d/%m/%y')
	scores = dict()
	for index,row in df.iterrows():
		if type(row['Date']) is float:
			continue
		if (datetime.strptime(row['Date'], '%d/%m/%y') > datet):
			break
		home = row['HomeTeam']
		away = row['AwayTeam']
		if home not in scores:
			scores[home] = 0
		if away not in scores:
			scores[away] = 0
		if row['FTR'] == 'H':
			scores[home] += 3
		elif row['FTR'] == 'A':
			scores[away] += 3
		else:
			scores[home] += 1
			scores[away] += 1
	rankings = []
	with open('data/standings/' + str(year) + 'Standings.csv', mode='w') as standing_files:
		standing_writer = csv.writer(standing_files, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		standing_writer.writerow(['Team', 'Points'])
		for key, value in reversed(sorted(scores.iteritems(), key=lambda (k,v): (v,k))):
			standing_writer.writerow([key, value])

for year in range(2006, 2018):
	getRankings(year, '31/12/' + str(year)[-2:])
