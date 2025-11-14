from nba_api.live.nba.endpoints.odds import Odds

# instantiate
odds_endpoint = Odds()

# fetch data
odds_response = odds_endpoint.get_dict()  # returns a Python dict

# iterate games
for game in odds_response.get('games', []):
    game_id = game.get('gameId')
    home_team = game.get('homeTeam', {}).get('teamName')
    away_team = game.get('awayTeam', {}).get('teamName')
    moneyline_home = game.get('odds', {}).get('moneylineHome')
    moneyline_away = game.get('odds', {}).get('moneylineAway')
    spread_home = game.get('odds', {}).get('spreadHomeValue')
    spread_home_odds = game.get('odds', {}).get('spreadHomeOdds')
    total = game.get('odds', {}).get('totalValue')
    total_over_odds = game.get('odds', {}).get('totalOverOdds')
    
    print(f"{away_team} @ {home_team} | ML: {moneyline_away}/{moneyline_home} | Spread: {spread_home} ({spread_home_odds}) | Total: {total} O:{total_over_odds}")