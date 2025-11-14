from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.live.nba.endpoints import scoreboard
from nba_api.live.nba.endpoints import Odds

import pandas as pd
import json
import difflib
import random
from datetime import datetime, timezone
from dateutil import parser

def get_teams(): 
    inputTeams = []
    while True:
        matchesFull = []
        input_name = input("Enter Team Name: ")

        # Try substring matching first
        matchesFull = [
            p for p in teams.get_teams()
            if input_name.lower() in p['full_name'].lower()
        ]

        # If no substring matches, fall back to fuzzy matching
        if not matchesFull:
            matchesFull = [
                p for p in teams.get_teams()
                if difflib.SequenceMatcher(None, input_name.lower(), p['full_name'].lower()).ratio() > 0.6
            ]
        if matchesFull:
            inputTeams.append(matchesFull[0])
            if len(inputTeams) == 2:
                break
        else:
            print("No matching team found. Please try again.")
            continue
    team1, team2 = inputTeams
    return team1, team2 

def findGameId(team1_id, team2_id):
    f = "{gameId}: {awayTeam} @ {homeTeam}  {gameTimeLTZ}" 
    game_id = None
    for game in games:
        gameTimeLTZ = parser.parse(game["gameTimeUTC"]).replace(tzinfo=timezone.utc).astimezone(tz=None)
        if (game['awayTeam']['teamId'] == team1_id and game['homeTeam']['teamId'] == team2_id) or (game['awayTeam']['teamId'] == team2_id and game['homeTeam']['teamId'] == team1_id):
            print("Match Found!")
            print(f.format(gameId=game['gameId'], awayTeam=game['awayTeam']['teamName'], homeTeam=game['homeTeam']['teamName'], gameTimeLTZ=gameTimeLTZ))
            print(f"Game ID: {game['gameId']}")
            game_id = game['gameId']
            home = game['homeTeam']['teamName']
            away = game['awayTeam']['teamName']
    if not game_id:
        print("No scheduled game found between the selected teams today.")
        exit()
    return game_id, home, away

def get_game_odds(gameID, home, away):
    odds = Odds()
    games_list = odds.get_games().get_dict()
    for game in games_list:
        if game['gameId'] == gameID:
            for market in game['markets']:
                for book in market['books']:
                    if book['countryCode'] == 'US' and market['name'] == '2way':
                        print(f"Book: {book['name']}")
                        for outcome in book['outcomes']:
                            if outcome['type'] == 'home':
                                outcome['type'] = home
                            elif outcome['type'] == 'away':
                                outcome['type'] = away
                            print(f"{outcome['type']}: {outcome['odds']}")



board = scoreboard.ScoreBoard()
games = board.games.get_dict()
print("See all Odds, or 1 game?")
input = input("1: All Odds\n2: 1 Game\n")
print("-----")
if input == "1":
    for game in games:
        get_game_odds(game['gameId'], game['homeTeam']['teamName'], game['awayTeam']['teamName'])
        print("-----")
elif input == "2":
    team1, team2 = get_teams()
    print(f"Team 1: {team1['full_name']}")
    print(f"Team 2: {team2['full_name']}")
    team1_id = team1['id']
    team2_id = team2['id']
    gameID, home, away = findGameId(team1_id, team2_id)



