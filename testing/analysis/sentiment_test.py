import sqlite3

from analysis.analysis import sentiment_label

# Constants hard coded to match dummy test database
VERY_NEGATIVE = 40
NEGATIVE = 50
NEUTRAL = 60
POSITIVE = 70
VERY_POSITIVE = 80

BUFFER = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"


def run(show_pass=False, show_fail=True, narrate=True):
    conn = sqlite3.connect("testing/analysis/data/dummy.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Articles;")

    if narrate:
        print("Starting Sentiment Test")
        print(BUFFER)

    fails = 0
    tests = 0
    while True:
        record = cursor.fetchone()
        if record is None:  # No more records
            break
        else:
            tests = tests + 1  # Increment test count

        # Extract data from record
        # NOTE: Column indexes are hard coded
        # title = record[0]
        text = record[1]
        articleID = record[2]
        lowerSentiment = record[3]
        upperSentiment = record[4]

        result = sentiment_label(text)
        result_label = result["label"]
        result_score = result["score"]
        result_sentiment = convert_label_to_value(result_label)
        lowerSentimentLabel = convert_value_to_label(lowerSentiment)
        upperSentimentLabel = convert_value_to_label(upperSentiment)

        # Do and print test result
        if result_sentiment >= lowerSentiment and result_sentiment <= upperSentiment:
            if show_pass:
                print("\033[092m", end="")  # Green
                print("Test Passed")
                print("Article ID: ", articleID)
                print_sentiment_debug(
                    lowerSentimentLabel, upperSentimentLabel, result_label, result_score
                )
                print("\033[0m", end="")
                print(BUFFER)
        else:
            if show_fail:
                print("\033[091m", end="")  # Red
                print("Test Failed")
                print("Article ID: ", articleID)
                print_sentiment_debug(
                    lowerSentimentLabel, upperSentimentLabel, result_label, result_score
                )
                print("\033[0m", end="")
                print(BUFFER)
            fails = fails + 1

    if narrate:
        print("End of Sentiment Test")
        print("Total Fails: ", fails)
        print("Total Tests: ", tests)

    return fails, tests


def print_sentiment_debug(
    lowerSentimentLabel, upperSentimentLabel, result_sentiment, result_score
):
    print(
        "Expected Sentiment between: ",
        lowerSentimentLabel,
        " and ",
        upperSentimentLabel,
    )
    print("Got Sentiment: ", result_sentiment)
    print("Got Score: ", result_score)


def convert_label_to_value(label):
    label = label.lower()
    if label == "very negative":
        return VERY_NEGATIVE
    elif label == "negative":
        return NEGATIVE
    elif label == "neutral":
        return NEUTRAL
    elif label == "positive":
        return POSITIVE
    elif label == "very positive":
        return VERY_POSITIVE
    else:
        return -1


def convert_value_to_label(value):
    if value == VERY_POSITIVE:
        return "Very Positive"
    elif value == POSITIVE:
        return "Positive"
    elif value == NEUTRAL:
        return "Neutral"
    elif value == NEGATIVE:
        return "Negative"
    elif value == VERY_NEGATIVE:
        return "Very Negative"
    else:
        return "error"
