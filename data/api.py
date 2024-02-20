import finnhub
import yfinance as yf
import asyncio
import concurrent.futures

from aiohttp import ClientSession
from os import getenv


class API:
    def __init__(self):
        # load api keys from env
        self.fn = finnhub.Client(api_key=getenv("FINNHUB_API_KEY"))
        self.NEWSCATCHER_API_KEY = getenv("NEWSCATCHER_API_KEY")
        self.ALPHAVANTAGE_API_KEY = getenv("ALPHAVANTAGE_API_KEY")
        self.NEWSAPI_API_KEY = getenv("NEWSAPI_API_KEY")

    async def get_company_info(self, symbol: str) -> dict:
        try:
            # first try to get the info from yfinance
            return yf.Ticker(symbol).info
        except:
            # if that fails, get the info from alphavantage
            async with ClientSession() as session:
                async with session.get(
                    f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={self.ALPHAVANTAGE_API_KEY}"
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {}

    async def get_stock_info(self, symbol: str) -> dict:
        try:
            # first try to get the info from yfinance
            # TODO: multithreading/async?
            ticker = yf.Ticker(symbol)
            return {
                "stock_day": ticker.history(period="1d", interval="1h").values,
                "stock_week": ticker.history(period="1wk", interval="1h").values,
                "stock_month": ticker.history(period="1mo", interval="1d").values,
                "stock_year": ticker.history(period="1y", interval="1w").values,
            }
        except:
            return {
                "stock_day": await self.get_stock_period(
                    symbol, "TIME_SERIES_INTRADAY", 24, "60min"
                ),
                "stock_week": await self.get_stock_period(
                    symbol, "TIME_SERIES_DAILY", 7
                ),
                "stock_month": await self.get_stock_period(
                    symbol, "TIME_SERIES_DAILY", 30
                ),
                "stock_year": await self.get_stock_period(
                    symbol, "TIME_SERIES_WEEKLY", 52
                ),
            }

    async def get_stock_period(
        self, symbol: str, period: str, num: int, interval=""
    ) -> list:
        # ping alphavantage for stock data
        url = (
            f"https://www.alphavantage.co/query?function={period}&symbol={symbol}&interval={interval}&apikey={self.ALPHAVANTAGE_API_KEY}"
            if period == "TIME_SERIES_INTRADAY"
            else f"https://www.alphavantage.co/query?function={period}&symbol={symbol}&apikey={self.ALPHAVANTAGE_API_KEY}"
        )
        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200 and not response.content == "":
                    data = await response.json()
                    keys = [key for key in data.keys() if "Time Series" in key]
                    return data[keys[0]]["4. close"][:num]
                else:
                    return {}
