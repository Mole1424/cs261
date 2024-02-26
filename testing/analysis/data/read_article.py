# This script should be ran directly from folder location (can be F5).
# Given an article id, it will copy the article text to the clipboard.
# This is a makeshift way to get the article text without opening dummy.db.
# Alternatively, you can open dummy.db using a sqlite browser. That will allow for you to add your own test data too.
# This is written solely for debugging sentiment_test results.

import sqlite3
import os
import pyperclip

DUMMY_DB = os.path.join(os.path.dirname(__file__), 'dummy.db')

conn = sqlite3.connect(DUMMY_DB)
cursor = conn.cursor()
id = input("Enter article ID: ")
cursor.execute("SELECT * FROM Articles WHERE ArticleID = ?", (id,))
record = cursor.fetchone()
if record is None:
    print("No article with that ID")
    exit()
text = record[1] # Article text is index 1 (hardcoded)
pyperclip.copy(text) # Copy to clipboard
print(record)
print("=====================================")
print("Article Text copied to clipboard")