import numpy as np
from typing import Dict, Any
from typing import List

# Sentiment Analysis Modules
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Content Recommendation Modules
import numpy as np
import pandas as pd
from implicit.als import AlternatingLeastSquares
from sklearn.model_selection import train_test_split
import scipy.sparse as sp

def sentiment_label(text) -> Dict[str, Any]: 
    """Returns a dictionary with the appropriate label and score for the text"""
    sid = SentimentIntensityAnalyzer()
    analysis = sid.polarity_scores(text)
    score = analysis["compound"]
    
    if (score >= 0.6):
        label = "Very Positive"
    elif (score >= 0.2):
        label = "Positive"
    elif (score >= -0.2):
        label = "Neutral"
    elif (score >= -0.6):
        label = "Negative"
    else:
        label = "Very Negative"

    return {"Score": score, "Label": label}    

def recommend_soft(k, user, stocks) -> List[int]:
    """Given a user and several other stocks vectors recommend the top k ones based off euclidian distance"""

    user = np.array(user)
    stocks = np.array(stocks)

    # Similarity based off euclidian distance
    distances = np.linalg.norm(stocks - user, axis=1)

    # Sort entries
    sorted_indices = np.argsort(distances)

    return sorted_indices[:k].tolist()


def recommend_hard_train(feedback):

    data = {'UserID': feedback[0], 'StockID': feedback[1], 'following': feedback[2]}
    df = pd.DataFrame(data)

    sparse_data = sp.csr_matrix((df['following'].astype(float), (df['UserID'], df['StockID'])))

    # train_data, test_data = train_test_split(sparse_data, test_size=0.2, random_state=15)

    model = AlternatingLeastSquares(factors=10, regularization=0.1, iterations=50)
    model.fit(sparse_data)

    # For Testing purposes
    """total_error = 0
    count = 0
    for user, item, true_rating in zip(test_data.row, test_data.col, test_data.data):
        predicted_rating = model.predict(user, item)
        error = (true_rating - predicted_rating) ** 2
        total_error += error
        count += 1

    rmse = np.sqrt(total_error / count)"""

    # still need to store the model
    return model

    # Recommend items for a specific user
def recommend_hard(model, userids, feedback, k):
    data = {'UserID': feedback[0], 'StockID': feedback[1], 'following': feedback[2]}
    df = pd.DataFrame(data)

    sparse_data = sp.csr_matrix((df['following'].astype(float), (df['UserID'], df['StockID'])))
    print(sparse_data)

    items, scores = model.recommend(userids, sparse_data[userids])

    return items[:k]
            

# example usage
# Say user 1 follows stocks 1,2,5
# user 2 only follows stock 3
# user 3 follows stock 3,4
# feedback is of the form
# following examples recommends for user 2
# feedback = [[1,1,1,1,1,2,2,2,2,3,3,3,3],[1,2,3,4,5,1,2,3,4,3,4,6,7],[1,1,1,1,1,1,1,1,1,1,1,1,1]] # Note the last string is always ones since only followings are taken into account
# model = recommend_hard_train(feedback)
# print(recommend_hard(model, 2, feedback, 3))