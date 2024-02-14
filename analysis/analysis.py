# Sentiment Analysis Modules
from nltk import download as nltk_download
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Content Recommendation Modules
import numpy as np
import pandas as pd
from implicit.als import AlternatingLeastSquares
from sklearn.model_selection import train_test_split
from scipy.sparse import coo_matrix

nltk_download('vader_lexicon')


def sentiment_label(text: str) -> dict:
    """Returns a dictionary with the appropriate label and score for the text."""
    sid = SentimentIntensityAnalyzer()
    analysis = sid.polarity_scores(text)
    score = analysis["compound"]

    return {"score": score, "label": sentiment_score_to_text(score)}


def sentiment_score_to_text(score: float) -> str:
    """Given a sentiment score, return the appropriate label."""
    if score >= 0.6:
        return "Very Positive"
    if score >= 0.2:
        return "Positive"
    if score >= -0.2:
        return "Neutral"
    if score >= -0.6:
        return "Negative"

    return "Very Negative"


def recommend_soft(k, user, stocks):
    """Given a user and several other stocks vectors recommend the top k ones based off euclidian distance."""

    user = np.array(user)
    stocks = np.array(stocks)

    # Similarity based off euclidian distance
    distances = np.linalg.norm(stocks - user, axis=1)

    # Sort entries
    sorted_indices = np.argsort(distances)

    return sorted_indices[:k].tolist()


# TODO
def recommend_hard_train(feedback):
    data = {'user_id': feedback[0], 'stock_id': feedback[1], 'following': feedback[2]}
    df = pd.DataFrame(data)

    sparse_data = coo_matrix((df['following'].astype(float), (df['user_id'], df['stock_id'])))

    train_data, test_data = train_test_split(sparse_data, test_size=0.2, random_state=15)

    model = AlternatingLeastSquares(factors=10, regularization=0.1, iterations=50)
    model.fit(train_data)

    # For Testing purposes
    """
    total_error = 0
    count = 0
    for user, item, true_rating in zip(test_data.row, test_data.col, test_data.data):
        predicted_rating = model.predict(user, item)
        error = (true_rating - predicted_rating) ** 2
        total_error += error
        count += 1

    rmse = np.sqrt(total_error / count)
    """

    # still need to store the model

    # Recommend items for a specific user


def recommend_hard(model, feedback, k, userid):
    return model.recommend(userid, feedback, N=k)
