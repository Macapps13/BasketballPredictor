from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.live.nba.endpoints import scoreboard
from nba_api.live.nba.endpoints import Odds
from nba_api.stats.endpoints import teamestimatedmetrics

from oddsCalc import generate_odds, win_prob_logistic, win_prob_normal

import pandas as pd
import json
import difflib
import random
from datetime import datetime, timezone
from dateutil import parser
import math

def get_teams(): 
    inputTeams = []
    while True:
        matchesFull = []
        input_name = input("Enter Team Name: ")

        # Try substring matching first
        matchesFull = [
            p for p in teamList
            if input_name.lower() in p['full_name'].lower()
        ]

        # If no substring matches, fall back to fuzzy matching
        if not matchesFull:
            matchesFull = [
                p for p in teamList
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
                    if (book['countryCode'] == 'AU' or book['countryCode'] == 'US') and market['name'] == '2way':
                        print(f"Book: {book['name']}")
                        for outcome in book['outcomes']:
                            if outcome['type'] == 'home':
                                outcome['type'] = home
                            elif outcome['type'] == 'away':
                                outcome['type'] = away
                            print(f"{outcome['type']}: {outcome['odds']}")
            ratings = teamestimatedmetrics.TeamEstimatedMetrics()
            ratings_df = ratings.get_data_frames()[0]
            homeID = game['homeTeamId']
            awayID = game['awayTeamId']
            home_net = ratings_df.loc[ratings_df['TEAM_ID'] == int(homeID), 'E_NET_RATING'].iloc[0]
            away_net = ratings_df.loc[ratings_df['TEAM_ID'] == int(awayID), 'E_NET_RATING'].iloc[0]
            print(f"Estimated Net Ratings - {home}: {home_net}, {away}: {away_net}")
            if home_net > away_net:
                print(f"Predicted Winner: {home}")
            elif away_net > home_net:
                print(f"Predicted Winner: {away}")
            print("ENR Diff:", abs(home_net - away_net))
            wp_logistic = win_prob_logistic(abs(home_net - away_net))
            wp_normal = win_prob_normal(abs(home_net - away_net))
            print("Win Probability: " + f"Logistic Model: {wp_logistic*100:.2f}%, Normal Model: {wp_normal*100:.2f}%")
            calcOdds = generate_odds((wp_logistic + wp_normal) / 2)
            fair = calcOdds["fair_decimal"]
            market = calcOdds["market_decimal"]
            print("Odds: Fair: ", fair, " Market: ", market)
            append_result_to_file(away, home, home if home_net - away_net > 0 else away, ((wp_logistic + wp_normal) / 2) * 100)

def append_result_to_file(away, home, team_name, win_percentage):
    """Append game result and win probability to resultsNBA.txt"""
    game_str = f"{away} @ {home}"
    win_str = f"{team_name} Win ({win_percentage:.2f}%)"
    with open("resultsNBA.txt", "a") as f:
        f.write(f"{game_str} - {win_str}\n")

teamList = teams.get_teams()
board = scoreboard.ScoreBoard()
games = board.games.get_dict()

def main():
    menu = input("1: All Odds\n2: 1 Game\n3: Exit\n")
    print("-----")
    if menu == "1":
        for game in games:
            get_game_odds(game['gameId'], game['homeTeam']['teamName'], game['awayTeam']['teamName'])
            print("-----")
    elif menu == "2":
        team1, team2 = get_teams()
        print(f"Team 1: {team1['full_name']}")
        print(f"Team 2: {team2['full_name']}")
        team1_id = team1['id']
        team2_id = team2['id']
        gameID, home, away = findGameId(team1_id, team2_id)
        get_game_odds(gameID, home, away)

    elif menu == "3":
        exit()
    else:
        print("Invalid input")
    main()
if __name__ == "__main__":
    main()






