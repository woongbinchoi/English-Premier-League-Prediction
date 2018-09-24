
import ntpath
import os
import pandas as pd
import math
from datetime import datetime

def getScore(team1, team2, date):
	datet = datetime.strptime(date, '%d/%m/%y')
	score = [0, 0, 0]
	for year in range(2006, 2019):
		path = 'data/cleaned/%s-%s.csv' % (year, year + 1)
		df = pd.read_csv(path)
		for index,row in df.iterrows():
			if datet < datetime.strptime(row['Date'], '%d/%m/%y'):
				return score
			if team1 == row['HomeTeam'] and team2 == row['AwayTeam']:
				if row['FTR'] == 'H':
					score[0] += 1
				elif row['FTR'] == 'A':
					score[1] += 1
				else:
					score[2] += 1
			elif team1 == row['AwayTeam'] and team2 == row['HomeTeam']:
				if row['FTR'] == 'A':
					score[0] += 1
				elif row['FTR'] == 'H':
					score[1] += 1
				else:
					score[2] += 1
	return score


def getAllTime():
	scores = dict()
	for year in range(2006, 2019):
	    path = 'data/cleaned/%s-%s.csv' % (year, year + 1)
	    df = pd.read_csv(path)
	    for index,row in df.iterrows():
	    	away = row['AwayTeam']
	    	home = row['HomeTeam']
	    	if type(away) is float:
	    		break
	    	swapped = False
	    	if away < home:
	    		key = away + "-" + home
	    	else:
	    		key = home + "-" + away
	    		swapped = True
	    	if key not in scores:
	    		scores[key] = [0, 0, 0];
	    	score = scores[key]
	    	if row['FTR'] == 'D':
	    		score[2] += 1
	    	elif (row['FTR'] == 'A' and not swapped) or (row['FTR'] == 'H' and swapped):
	    		score[0] += 1
	    	else:
	    		score[1] += 1
	for key in scores:
		print key
		print scores[key]
	return scores
