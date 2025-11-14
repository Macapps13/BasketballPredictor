from oddsCalc import generate_odds
from outcome import win_prob_logistic, win_prob_normal

home_net = input("Enter Home Team Net Rating: ")
away_net = input("Enter Away Team Net Rating: ")

wp_logistic = win_prob_logistic(abs(float(home_net) - float(away_net)))
wp_normal = win_prob_normal(abs(float(home_net) - float(away_net)))
if home_net > away_net:
    print("Predicted Winner: Home Team")
elif away_net > home_net:
    print("Predicted Winner: Away Team")
print("NR Differential: ", abs(float(home_net) - float(away_net)))
print("Win Probability: " + f"Logistic Model: {wp_logistic*100:.2f}%, Normal Model: {wp_normal*100:.2f}%")
calcOdds = generate_odds((wp_logistic + wp_normal) / 2)
fair = calcOdds["fair_decimal"]
market = calcOdds["market_decimal"]
print("Odds: Fair: ", fair, " Market: ", market)
