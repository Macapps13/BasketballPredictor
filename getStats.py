from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.live.nba.endpoints import scoreboard
from nba_api.live.nba.endpoints import Odds
from nba_api.stats.endpoints import teamestimatedmetrics
from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.endpoints import teamgamelogs

import pandas as pd
import json
import difflib
import random
from datetime import datetime, timezone
from dateutil import parser
import math


def get_stats(teamID):
    estRatings = teamestimatedmetrics.TeamEstimatedMetrics()
    stats = leaguedashteamstats.LeagueDashTeamStats()
    gameLogHome = teamgamelogs.TeamGameLogs(
    team_id_nullable=teamID,
    season_nullable="2025-26",
    season_type_nullable="Regular Season"
    )
    gameLogHome_df = gameLogHome.get_data_frames()[0]
    print(gameLogHome_df.head())
    gameLogHome_df['GAME_DATE'] = pd.to_datetime(gameLogHome_df['GAME_DATE'])
    gameLogHome_df = gameLogHome_df.sort_values('GAME_DATE')
    last5 = gameLogHome_df.tail(5)
    avg_pm_last5 = last5['PLUS_MINUS'].mean()
    ratings_df = estRatings.get_data_frames()[0]
    stats_df = stats.get_data_frames()[0]
    wpct = stats_df.loc[stats_df['TEAM_ID'] == int(teamID), 'W_PCT'].iloc[0]
    net = ratings_df.loc[ratings_df['TEAM_ID'] == int(teamID), 'E_NET_RATING'].iloc[0]
    
    print(f"Team ID: {teamID}")
    print(f"Win Percentage: {wpct:.3f}")
    print(f"Net Rating: {net:.3f}")
    print(f"Average Plus/Minus Last 5 Games: {avg_pm_last5:.3f}")
    return [wpct, net, avg_pm_last5]

home_matrix = get_stats(1610612764)
away_matrix = get_stats(1610612761)
M = []
for i in range(len(home_matrix)):
    M.append(home_matrix[i] - away_matrix[i])
print(M)

