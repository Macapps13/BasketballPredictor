from flask import Flask, jsonify
from nba_api.stats.static import teams
from nba_api.live.nba.endpoints import scoreboard
from nba_api.live.nba.endpoints import Odds
from nba_api.stats.endpoints import teamestimatedmetrics

from oddsCalc import generate_odds, win_prob_logistic, win_prob_normal

from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

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

            wp_logistic = win_prob_logistic(abs(home_net - away_net))
            wp_normal = win_prob_normal(abs(home_net - away_net))

            calcOdds = generate_odds((wp_logistic + wp_normal) / 2)
            fair = calcOdds["fair_decimal"]
            market = homeOdds if homeOdds < awayOdds else awayOdds

            return {
                "gameId": gameID,
                "home": home,
                "away": away,
                "fairOdds": fair,
                "marketOdds": market,
                "logisticWinProb": wp_logistic,
                "normalWinProb": wp_normal,
            }

    return {"error": "Game not found"}


@app.route("/run")
def run():
    teamList = teams.get_teams()
    board = scoreboard.ScoreBoard()
    games = board.games.get_dict()

    results = []

    for g in games:
        res = get_game_odds(
            g['gameId'],
            g['homeTeam']['teamName'],
            g['awayTeam']['teamName']
        )
        results.append(res)

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)