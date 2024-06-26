from datetime import datetime, timedelta
from os import getenv

import yfinance as yf
from aiohttp import ClientSession
from newspaper import Article


async def get_company_info(symbol: str) -> dict:
    """Get company info given a stock symbol.
    Returns a dictionary with the company's name, website, description, location, market cap, CEO, and sector.
    If the company is not found, returns an empty dictionary."""
    try:
        # first try to get the info from yfinance
        info = yf.Ticker(symbol).info
        ceo = info.get("companyOfficers", "")
        ceo = (
            ceo[0].get("name", "") if len(ceo) > 0 else ""
        )  # get the first board member's name
        return {
            "name": info.get("longName", ""),  # use info.get() to avoid key errors
            "url": info.get("website", ""),
            "description": info.get("longBusinessSummary", ""),
            "location": f"{info.get('address1', '')} {info.get('city', '')} {info.get('state', '')} {info.get('country', '')}",
            "market_cap": info.get("marketCap", ""),
            "ceo": ceo,
            "sector": info.get("sector", ""),
        }

    except:
        # if that fails, get the info from alphavantage
        async with ClientSession() as session:
            async with session.get(
                f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={getenv('ALPHAVANTAGE_API_KEY')}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "name": data.get("Name", ""),
                        "url": "",  # no website info (or ceo) :(
                        "description": data.get("Description", ""),
                        "location": data.get("Address", "").capitalize(),
                        "market_cap": data.get("MarketCapitalization", ""),
                        "ceo": "",
                        "sector": data.get("Sector", "").capitalize(),
                    }
                else:
                    return {}


async def get_stock_info(symbol: str) -> dict:
    """Get stock info given a stock symbol.
    Returns a dictionary with the stock's price, open, high, low, volume, and previous close.
    If the stock is not found, returns an empty dictionary."""
    try:
        # first try to get the info from yfinance
        # TODO: multithreading/async?
        ticker = yf.Ticker(symbol)
        return {
            "stock_day": (
                # get the last 24 hours of stock data (need to use 5d interval as 1d cuts off at midnight)
                ticker.history(period="5d", interval="1h")["Close"].to_list()[-24:]
                if len(ticker.history(period="5d", interval="1h")) > 0
                else []  # if no data, return an empty list
            ),
            "stock_week": (
                ticker.history(period="5d", interval="1h")["Close"].to_list()
                if len(ticker.history(period="5d", interval="1h")) > 0
                else []
            ),
            "stock_month": (
                ticker.history(period="1mo", interval="1d")["Close"].to_list()
                if len(ticker.history(period="1mo", interval="1d")) > 0
                else []
            ),
            "stock_year": (
                ticker.history(period="1y", interval="1wk")["Close"].to_list()
                if len(ticker.history(period="1y", interval="1wk")) > 0
                else []
            ),
            "market_cap": ticker.info.get("marketCap", ""),
            "exchange": ticker.info.get("exchange", ""),
        }
    except:
        market_cap, exchange = await get_market_cap_and_exchange(symbol)
        return {
            "stock_day": await get_stock_period(
                symbol, "TIME_SERIES_INTRADAY", 24, "60min"
            ),
            "stock_week": await get_stock_period(symbol, "TIME_SERIES_DAILY", 7),
            "stock_month": await get_stock_period(symbol, "TIME_SERIES_DAILY", 30),
            "stock_year": await get_stock_period(symbol, "TIME_SERIES_WEEKLY", 52),
            "market_cap": market_cap,
            "exchange": exchange,
        }


async def get_stock_period(symbol: str, period: str, num: int, interval="") -> list:
    """Get stock info for a given period."""
    # ping alphavantage for stock data
    url = (
        f"https://www.alphavantage.co/query?function={period}&symbol={symbol}&interval={interval}&apikey={getenv('ALPHAVANTAGE_API_KEY')}"
        if period == "TIME_SERIES_INTRADAY"
        else f"https://www.alphavantage.co/query?function={period}&symbol={symbol}&apikey={getenv('ALPHAVANTAGE_API_KEY')}"
    )
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                keys = [
                    key for key in data.keys() if "Time Series" in key
                ]  # get the time series key

                return (
                    [
                        float(entry["4. close"])  # only get close prive
                        for entry in list(data[keys[0]].values())[
                            :num
                        ]  # get the last num entries
                    ]
                    if len(keys) > 0
                    else []
                )
            else:
                return []


async def get_market_cap_and_exchange(symbol: str) -> tuple[float, str]:
    async with ClientSession() as session:
        async with session.get(
            f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={getenv('ALPHAVANTAGE_API_KEY')}"
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("MarketCapitalization", 0), data.get("Exchange", "")
            else:
                return 0, ""


async def get_news(name: str) -> list[dict]:
    """Get news articles for a given company name."""

    # read the news sources whitelist
    with open("data/news_whitelist.csv", "r") as f:
        whitelist = "".join([line.strip() for line in f.readlines()])

    articles = []
    try:
        async with ClientSession(
            headers={"x-api-key": getenv("NEWSCATCHER_API_KEY")}
        ) as session:
            # get the date 1 year ago (newscatcher only allows 1 year of data)
            time = (datetime.now() - timedelta(days=364)).strftime("%Y/%m/%d")
            url = f"https://api.newscatcherapi.com/v2/search?q={name}&lang=en&sources={whitelist}&sort_by=date&page_size=50&from={time}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    for article in data["articles"]:
                        articles.append(
                            {
                                "url": article["link"],
                                "headline": article["title"],
                                "publisher": article["clean_url"],
                                "date": datetime.strptime(
                                    article["published_date"], "%Y-%m-%d %H:%M:%S"
                                ),
                                "summary": article["excerpt"],
                                "full_text": article["summary"],  # full text for speed
                            }
                        )
    except:
        # if cant use newscatcher, use newsapi
        num_articles = 50 - len(articles)  # get the remaining articles
        async with ClientSession() as session:
            url = f'https://newsapi.org/v2/everything?q={name}&language=en&domains={whitelist}&pageSize={num_articles}&apiKey={getenv("NEWSAPI_API_KEY")}'
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    for article in data["articles"]:
                        # first paragraph of the article as summary
                        summary = get_article_content(article["url"]).split("\n")[0]
                        articles.append(
                            {
                                "url": article["url"],
                                "headline": article["title"],
                                "publisher": article["source"]["name"],
                                "date": datetime.strptime(
                                    article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                                ),
                                "summary": summary,
                                "full_text": get_article_content(article["url"]),
                            }
                        )
    return articles


async def search_companies(query: str) -> list[tuple[str, str]]:
    """Search for companies given a query."""
    async with ClientSession() as session:
        async with session.get(
            f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
        ) as response:
            if response.status == 200:
                data = await response.json()

                result_list = []
                for result in data["quotes"][:20]:  # only get the first 20 results
                    try:
                        longname = result["longname"]
                        if longname != "":  # only add if longname is not empty
                            result_list.append((result["longname"], result["symbol"]))
                    except Exception:
                        pass
                return result_list
            else:
                return []


async def get_symbols(name: str) -> list[str]:
    """Get stock symbols given a company name."""

    async with ClientSession() as session:
        async with session.get(
            f"https://query2.finance.yahoo.com/v1/finance/search?q={name}"
        ) as response:
            tickers = []
            if response.status == 200:
                data = await response.json()
                # get the first result's long and short name
                first_result_long = (
                    data["quotes"][0]["longname"].lower()
                    if data["quotes"][0]["longname"]
                    else ""
                )
                first_result_short = (
                    data["quotes"][0]["shortname"].lower()
                    if data["quotes"][0]["shortname"]
                    else ""
                )
                for quote in data["quotes"]:
                    # if the long or short name matches the first result, add the ticker
                    if (
                        "longname" in quote
                        and quote["longname"].lower() == first_result_long
                    ) or (
                        "shortname" in quote
                        and quote["shortname"].lower() == first_result_short
                    ):
                        tickers.append(quote["symbol"])
                        # update the first result's long and short name if it's empty
                        if "longname" in quote:
                            first_result_long = quote["longname"].lower()
                        if "shortname" in quote:
                            first_result_short = quote["shortname"].lower()
                if len(tickers) > 0:
                    return tickers
                else:
                    return []
            else:
                return []


def get_article_content(url: str) -> str:
    """Get the text of an article given its url."""
    try:
        # use newspaper4 to get the article text
        article = Article(url, language="en")
        article.download()
        article.parse()
        return article.text
    except:
        return ""
