import pandas as pd
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss
import joblib
import os

MODEL_PATH = "nba_live_model.joblib"
DATA_PATH = "games_dataset.csv"   


def load_dataset():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=[
            "net_rating_diff", "winpct_diff", "pm5_diff", "home_win"
        ])
        df.to_csv(DATA_PATH, index=False)
        return df
    return pd.read_csv(DATA_PATH)


def initialize_or_load_model(df):
    """
    Loads existing model or trains a new SGDClassifier (supports online learning).
    """
    if os.path.exists(MODEL_PATH):
        print("Loaded existing model.")
        return joblib.load(MODEL_PATH)

    print("No existing model found — training initial model...")

    if len(df) < 10:
        raise ValueError("Need at least 10 games to start training.")

    X = df[["net_rating_diff", "winpct_diff", "pm5_diff"]].values
    y = df["home_win"].values

    # Create online-learning logistic regression
    model = SGDClassifier(
        loss="log_loss",        # logistic regression
        max_iter=1000,
        learning_rate="optimal"
    )

    # partial_fit requires specifying all possible classes once
    model.partial_fit(X, y, classes=[0, 1])

    joblib.dump(model, MODEL_PATH)
    print("Initial model trained and saved.")
    return model


def evaluate_model(model, df):
    """Evaluate on a held-out test split."""
    if len(df) < 20:
        print("Not enough data to evaluate yet.")
        return

    X = df[["net_rating_diff", "winpct_diff", "pm5_diff"]].values
    y = df["home_win"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)

    acc = accuracy_score(y_test, preds)
    ll = log_loss(y_test, probs)

    print("\n===== MODEL EVALUATION =====")
    print(f"Accuracy: {acc:.3f}")
    print(f"Log Loss: {ll:.3f}")


def predict_games(model, games_today):
    """
    Predict a list of games like:
    [
        {"home_team": "...", "away_team": "...",
         "net_rating_diff": x, "winpct_diff": y, "pm5_diff": z}
    ]
    """
    df = pd.DataFrame(games_today)
    X = df[["net_rating_diff", "winpct_diff", "pm5_diff"]].values

    probs = model.predict_proba(X)[:, 1]
    preds = (probs >= 0.5).astype(int)

    df["home_win_prob"] = probs
    df["home_win_pred"] = preds

    print("\n===== PREDICTIONS =====")
    for _, row in df.iterrows():
        ht = row["home_team"]
        at = row["away_team"]
        p = row["home_win_prob"]
        pred = "HOME" if row["home_win_pred"] == 1 else "AWAY"
        print(f"{at} @ {ht} → P(Home)={p:.3f} → Predict: {pred}")

    return df


def update_model_with_result(model, game_row):
    """
    Updates the model with ONE finished game result.
    game_row = {
        "net_rating_diff": ...,
        "winpct_diff": ...,
        "pm5_diff": ...,
        "home_win": 0 or 1
    }
    """
    df_row = pd.DataFrame([game_row])
    X = df_row[["net_rating_diff", "winpct_diff", "pm5_diff"]].values
    y = df_row["home_win"].values

    model.partial_fit(X, y)  
    joblib.dump(model, MODEL_PATH)

    print("Model updated with new result.")


def append_result_to_dataset(game_row):
    df = load_dataset()
    df = pd.concat([df, pd.DataFrame([game_row])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)
    print("Result added to dataset.")


if __name__ == "__main__":

    df = load_dataset()
    model = initialize_or_load_model(df)

    evaluate_model(model, df)

    # Predict today
    games = [
        {
            "home_team": "Lakers",
            "away_team": "Warriors",
            "net_rating_diff": 2.5,
            "winpct_diff": 0.08,
            "pm5_diff": 6.0
        }
    ]

    predict_games(model, games)

    # After real result:
    # final_result = {
    #     "net_rating_diff": 2.5,
    #     "winpct_diff": 0.08,
    #     "pm5_diff": 6.0,
    #     "home_win": 1
    # }
    #
    # append_result_to_dataset(final_result)
    # update_model_with_result(model, final_result)