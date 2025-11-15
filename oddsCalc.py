import math
from scipy.stats import norm
from fractions import Fraction

def generate_odds(p, vig=0.05):
    """
    Takes model probability p (0<p<=1) and generates:
    - Fair decimal odds (1/p)
    - Market decimal odds with vig applied
    - Market fractional odds (simplified)
    - Market American odds
    - Market implied probability after vig
    """

    if p <= 0 or p > 1:
        raise ValueError("p must be in (0,1].")

    # --- Fair odds ---
    fair_decimal = 1.0 / p

    # --- Apply uniform vig ---
    # Overround factor: O = 1 + vig
    O = 1.0 + vig
    q = p * O  # market implied probability (increases due to vig)
    market_decimal = 1.0 / q

    # --- Fractional odds ---
    if market_decimal <= 1:
        fractional = "0/1"
    else:
        frac = Fraction(market_decimal - 1).limit_denominator(1000)
        fractional = f"{frac.numerator}/{frac.denominator}"

    # --- American odds ---
    if market_decimal <= 1:
        american = 0
    elif market_decimal >= 2.0:
        american = int(round((market_decimal - 1) * 100))   # positive odds
    else:
        american = int(round(-100.0 / (market_decimal - 1)))  # negative odds

    return {
        "model_prob": round(p, 4),
        "fair_decimal": round(fair_decimal, 3),
        "market_decimal": round(market_decimal, 3),
        "market_fractional": fractional,
        "market_american": american,
        "market_implied_prob": round(q, 4)
    }

def win_prob_logistic(net_rating_diff, k=0.12):
    # Logistic model: P = 1 / (1 + exp(-k * D)), where D = net_rating_diff
    return 1 / (1 + math.exp(-k * net_rating_diff))


def win_prob_normal(net_rating_diff, pace=100, home_adv=0, sigma=12):
    # Normal model: convert net-rating diff → expected margin, then P = Φ((margin) / σ)
    margin = net_rating_diff * (pace / 100) + home_adv
    return norm.cdf(margin / sigma)