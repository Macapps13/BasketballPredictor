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


def get_stats(teamName):
    team = [team for team in teams.get_teams() if team['full_name'] == teamName][0]
    teamID = team['id']
    estRatings = teamestimatedmetrics.TeamEstimatedMetrics()
    stats = leaguedashteamstats.LeagueDashTeamStats()
    gameLogHome = teamgamelogs.TeamGameLogs(
    team_id_nullable=teamID,
    season_nullable="2025-26",
    season_type_nullable="Regular Season"
    )
    gameLogHome_df = gameLogHome.get_data_frames()[0]
    gameLogHome_df['GAME_DATE'] = pd.to_datetime(gameLogHome_df['GAME_DATE'])
    gameLogHome_df = gameLogHome_df.sort_values('GAME_DATE')
    last5 = gameLogHome_df.tail(5)
    avg_pm_last5 = last5['PLUS_MINUS'].mean()
    ratings_df = estRatings.get_data_frames()[0]
    stats_df = stats.get_data_frames()[0]
    wpct = stats_df.loc[stats_df['TEAM_ID'] == int(teamID), 'W_PCT'].iloc[0]
    net = ratings_df.loc[ratings_df['TEAM_ID'] == int(teamID), 'E_NET_RATING'].iloc[0]
    
    return [wpct, net, avg_pm_last5]

def make_matrix(team1_stats, team2_stats):
    matrix = []
    
    for i in range(len(team1_stats)):
        matrix.append(round(float(team1_stats[i] - team2_stats[i]), 3))
    print(matrix)
    return matrix


# make_matrix(get_stats("Orlando Magic"), get_stats("Golden State Warriors"))
# make_matrix(get_stats("Brooklyn Nets"), get_stats("Boston Celtics"))
# make_matrix(get_stats("Atlanta Hawks"), get_stats("Detroit Pistons"))
# make_matrix(get_stats("San Antonio Spurs"), get_stats("Memphis Grizzlies"))
make_matrix(get_stats("Los Angeles Lakers"), get_stats("Utah Jazz"))
make_matrix(get_stats("Portland Trail Blazers"), get_stats("Phoenix Suns"))




