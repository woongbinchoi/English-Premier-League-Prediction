import pandas as pd
import ntpath

# Calculate match played, current standing, goal for, goal against, goal difference
# Input is csv that is just cleaned from raw data
# Output is csv modified with each row added match played, current standing, GF, GA, GD 

def addCurrentDetails(cleanedPath):
	teamDetail = {}
	matchDetail = {
		'HT_match_played': [],
		'HT_current_standing': [],
		'HT_goal_for': [],
		'HT_goal_against': [],
		'HT_goal_differnece': [],
		'AT_match_played': [],
		'AT_current_standing': [],
		'AT_goal_for': [],
		'AT_goal_against': [],
		'AT_goal_differnece': []
	}
	df = pd.read_csv(cleanedPath)

	for index, row in df.iterrows():
		HT = row['HomeTeam']
		AT = row['AwayTeam']

		if HT not in teamDetail:
			teamDetail[HT] = {
				'match_played': 0,
				'current_standing': 0,
				'goal_for': 0,
				'goal_against': 0,
				'goal_difference': 0
			}
		if AT not in teamDetail:
			teamDetail[AT] = {
				'match_played': 0,
				'current_standing': 0,
				'goal_for': 0,
				'goal_against': 0,
				'goal_difference': 0
			}

		matchDetail['HT_match_played'].append(teamDetail[HT]['match_played'])
		matchDetail['HT_current_standing'].append(teamDetail[HT]['current_standing'])
		matchDetail['HT_goal_for'].append(teamDetail[HT]['goal_for'])
		matchDetail['HT_goal_against'].append(teamDetail[HT]['goal_against'])
		matchDetail['HT_goal_differnece'].append(teamDetail[HT]['goal_difference'])
		matchDetail['AT_match_played'].append(teamDetail[AT]['match_played'])
		matchDetail['AT_current_standing'].append(teamDetail[AT]['current_standing'])
		matchDetail['AT_goal_for'].append(teamDetail[AT]['goal_for'])
		matchDetail['AT_goal_against'].append(teamDetail[AT]['goal_against'])
		matchDetail['AT_goal_differnece'].append(teamDetail[AT]['goal_difference'])

		teamDetail[HT]['match_played'] += 1
		teamDetail[AT]['match_played'] += 1
		teamDetail[HT]['goal_for'] += row['FTHG']
		teamDetail[AT]['goal_for'] += row['FTAG']
		teamDetail[HT]['goal_against'] += row['FTAG']
		teamDetail[AT]['goal_against'] += row['FTHG']

		gd = row['FTHG'] - row['FTAG']
		teamDetail[HT]['goal_difference'] += gd
		teamDetail[AT]['goal_difference'] -= gd

		gameResult = row['FTR']
		if gameResult == 'H':
			teamDetail[HT]['current_standing'] += 3
		elif gameResult == 'A':
			teamDetail[AT]['current_standing'] += 3
		else: 
			teamDetail[HT]['current_standing'] += 1
			teamDetail[AT]['current_standing'] += 1

	df.set_index('MatchID', inplace=True)

	for key, matchResults in matchDetail.items():
		df[key] = pd.Series(matchResults, index=df.index)

	df.to_csv(cleanedPath)

def addCurrentDetailsAll(cleanedFolderPath):
	for year in range(1993, 2019):
		file = '%s-%s.csv' % (year, year + 1)
		path = ntpath.join(cleanedFolderPath, file)
		print("About to add 'current details' for " + path + " ...")
		addCurrentDetails(path)
	