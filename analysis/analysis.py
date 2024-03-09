# Content Recommendation Modules
import numpy as np
import pandas as pd
import scipy.sparse as sp
from implicit.als import AlternatingLeastSquares

# Sentiment Analysis Modules
from nltk import download as nltk_download
from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.model_selection import train_test_split

nltk_download("vader_lexicon")
nltk_download("punkt")


def sentiment_label(text: str) -> dict:
    """Returns a dictionary with the appropriate label and score for the text."""
    sid = SentimentIntensityAnalyzer()
    lines_list = tokenize.sent_tokenize(text)
    sid = SentimentIntensityAnalyzer()
    score = []
    for line in lines_list:
        analysis = sid.polarity_scores(line)
        score.append(analysis["compound"])

    score = np.mean(np.array(score))

    return {"score": score, "label": sentiment_score_to_text(score)}


def sentiment_score_to_text(score: float) -> str:
    """Given a sentiment score, return the appropriate label."""
    if score >= 0.5:
        return "Very Positive"
    if score >= 0.05:
        return "Positive"
    if score >= -0.05:
        return "Neutral"
    if score >= -0.5:
        return "Negative"

    return "Very Negative"