import finnhub as fn
import yfinance as yf

from aiohttp import ClientSession
from os import getenv


class API:
    def __init__(self):
        self.finnhub = fn.Client(api_key=getenv("FINNHUB_API_KEY"))
        self.ALPHAVANTAGE_API_KEY = getenv("ALPHAVANTAGE_API_KEY")
        self.NEWSAPI_API_KEY = getenv("NEWSAPI_API_KEY")
        self.NEWSCATCHER_API_KEY = getenv("NEWSCATCHER_API_KEY")
