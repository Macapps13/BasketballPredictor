import pandas as pd
from sklearn.linear_model import LogisticRegression
import numpy as np

# 1. Load your data (replace 'synthetic_nba_data.csv' with your actual file name)
df = pd.read_csv('games_dataset.csv') 

# 2. Prepare the data
# X contains the three features (differentials)
X = df[['net_rating_diff', 'winpct_diff', 'pm5_diff']]
# y contains the target variable (1 for home win, 0 for away win)
y = df['home_win']

# 3. Initialize and train the Logistic Regression model
# The C parameter controls regularization (a technique to prevent overfitting)
# A smaller dataset like yours can be prone to overfitting, so keep this default.
model = LogisticRegression(random_state=42)
model.fit(X, y)

print("Logistic Regression Model Trained Successfully.")

# 4. Make a prediction for a new, hypothetical game

# Example Game: Home Team favored with good differentials
# Features: Net_Rating_Diff=2.5, Win_Pct_Diff=0.08, Plus_Minus_Diff=4.0
new_game_features = np.array([[2.5, 0.08, 4.0]])

# Get the predicted probability
# predict_proba returns an array: [P(Away Win), P(Home Win)]
probabilities = model.predict_proba(new_game_features)

home_win_probability = probabilities[0, 1] * 100

# --- ADD THIS CODE ---
feature_names = ['net_rating_diff', 'winpct_diff', 'pm5_diff']
weights = model.coef_[0]
intercept = model.intercept_[0]

print("\n--- Learned Model Weights ---")
print(f"Intercept (Base Probability): {intercept:.4f}")

for name, weight in zip(feature_names, weights):
    print(f"Weight of {name}: {weight:.4f}")
print("------------------------------")
# ---------------------

print(f"\n--- Prediction for New Game ---")
print(f"Features (Net Rating, Win %, +/-): {new_game_features[0]}")
print(f"The predicted probability of the HOME team winning is: {home_win_probability:.2f}%")
print(f"The model predicts: {'Home Team Wins' if home_win_probability >= 50 else 'Away Team Wins'}")