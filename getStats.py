from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.live.nba.endpoints import scoreboard
from nba_api.live.nba.endpoints import Odds
from nba_api.stats.endpoints import teamestimatedmetrics
from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.endpoints import teamgamelog

import pandas as pd
import json
import difflib
import random
from datetime import datetime, timezone
from dateutil import parser
import math

def get_stats(homeID, awayID):
    estRatings = teamestimatedmetrics.TeamEstimatedMetrics()
    stats = leaguedashteamstats.LeagueDashTeamStats()
    gameLogHome = teamgamelog.TeamGameLog(team_id = "1610612742")
    gameLogHome_df = gameLogHome.get_data_frames()[0]
    print(gameLogHome_df.head())
   
    ratings_df = estRatings.get_data_frames()[0]
    stats_df = stats.get_data_frames()[0]
    home_wpct = stats_df.loc[stats_df['TEAM_ID'] == int(homeID), 'W_PCT'].iloc[0]
    away_wpct = stats_df.loc[stats_df['TEAM_ID'] == int(awayID), 'W_PCT'].iloc[0]
    wpct_diff = home_wpct - away_wpct
    home_net = ratings_df.loc[ratings_df['TEAM_ID'] == int(homeID), 'E_NET_RATING'].iloc[0]
    away_net = ratings_df.loc[ratings_df['TEAM_ID'] == int(awayID), 'E_NET_RATING'].iloc[0]
    net_diff = home_net - away_net
    print("Win Pct diff = " + str(wpct_diff))
    print("Net Rating diff = " + str(net_diff))
    return 

get_stats(1610612764, 1610612754)