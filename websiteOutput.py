from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.live.nba.endpoints import scoreboard
from nba_api.live.nba.endpoints import Odds
from nba_api.stats.endpoints import teamestimatedmetrics

from oddsCalc import generate_odds, win_prob_logistic, win_prob_normal
from getStats import save_matrix, get_stats, append_result_to_file

import pandas as pd
import json
import difflib
import random
from datetime import datetime, timezone
from dateutil import parser
import math

def get_game_odds(gameID, home, away):
    odds = Odds()
    games_list = odds.get_games().get_dict()
    for game in games_list:
        if game['gameId'] == gameID:
            for market in game['markets']:
                for book in market['books']:
                    if (book['countryCode'] == 'US') and market['name'] == '2way':
                        for outcome in book['outcomes']:
                            if outcome['type'] == 'home':
                                outcome['type'] = home
                                homeOdds = outcome['odds']
                            elif outcome['type'] == 'away':
                                outcome['type'] = away
                                awayOdds = outcome['odds']
            ratings = teamestimatedmetrics.TeamEstimatedMetrics()
            ratings_df = ratings.get_data_frames()[0]
            homeID = game['homeTeamId']
            awayID = game['awayTeamId']
            home_net = ratings_df.loc[ratings_df['TEAM_ID'] == int(homeID), 'E_NET_RATING'].iloc[0]
            away_net = ratings_df.loc[ratings_df['TEAM_ID'] == int(awayID), 'E_NET_RATING'].iloc[0]
            if home_net > away_net:
                print(f"Predicted Winner: {home}")
            elif away_net > home_net:
                print(f"Predicted Winner: {away}")
            wp_logistic = win_prob_logistic(abs(home_net - away_net))
            wp_normal = win_prob_normal(abs(home_net - away_net))
            print("Win Probability: " + f"Logistic Model: {wp_logistic*100:.2f}%, Normal Model: {wp_normal*100:.2f}%")
            calcOdds = generate_odds((wp_logistic + wp_normal) / 2)
            fair = calcOdds["fair_decimal"]
            market = homeOdds if homeOdds < awayOdds else awayOdds
            print("Odds: \nFair: ", fair)
            print("Market: ", market)

teamList = teams.get_teams()
board = scoreboard.ScoreBoard()
games = board.games.get_dict()

for games in games:
    get_game_odds(games['gameId'], games['homeTeam']['teamName'], games['awayTeam']['teamName'])
    print("-----")