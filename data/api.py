import finnhub
import yfinance as yf
from typing import Any

from aiohttp import ClientSession
from newscatcherapi import NewsCatcherApiClient
from os import getenv


class API:
    def __init__(self):
        self.fn = finnhub.Client(api_key=getenv("FINNHUB_API_KEY"))
        self.nca = NewsCatcherApiClient(x_api_key=getenv("NEWSCATCHER_API_KEY"))
        self.ALPHAVANTAGE_API_KEY = getenv("ALPHAVANTAGE_API_KEY")
        self.NEWSAPI_API_KEY = getenv("NEWSAPI_API_KEY")

    async def get_company_info(self, symbol: str) -> dict:
        try:
            data = yf.Ticker(symbol)
            info = data.info
            stock_day = data.history(period="1d", interval="1hr")
            stock_week = data.history(period="1wk", interval="1d")
            stock_month = data.history(period="1mo", interval="1d")
            stock_year = data.history(period="1y", interval="1wk")
            return {
                "info": info,
                "stock_day": stock_day,
                "stock_week": stock_week,
                "stock_month": stock_month,
                "stock_year": stock_year,
            }
        except:
            async with ClientSession() as session:
                async with session.get(
                    f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={self.ALPHAVANTAGE_API_KEY}"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                    else:
                        data = {}

                async with session.get(
                    f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=60min&apikey={self.ALPHAVANTAGE_API_KEY}"
                ) as response:
                    if response.status == 200:
                        stock_day = await response.json()
                    else:
                        stock_day = {}
