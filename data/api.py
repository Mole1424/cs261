import yfinance as yf

from aiohttp import ClientSession
from newspaper import Article
from os import getenv


async def get_company_info(symbol: str) -> dict:
    try:
        # first try to get the info from yfinance
        info = yf.Ticker(symbol).info
        return {
            "name": info.get("longName", ""),
            "url": info.get("website", ""),
            "description": info.get("longBusinessSummary", ""),
            "location": f"{info.get('address1', '')} {info.get('city', '')} {info.get('state', '')} {info.get('country', '')}",
            "marketCap": info.get("marketCap", ""),
            "ceo": info.get("companyOfficers", "")[0].get("name", ""),
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
                        "url": "",
                        "description": data.get("Description", ""),
                        "location": data.get("Address", ""),
                        "marketCap": data.get("MarketCapitalization", ""),
                        "ceo": "",
                    }
                else:
                    return {}


async def get_stock_info(symbol: str) -> dict:
    try:
        # first try to get the info from yfinance
        # TODO: multithreading/async?
        ticker = yf.Ticker(symbol)
        return {
            "stock_day": ticker.history(period="1d", interval="1h")["Close"].to_list(),
            "stock_week": ticker.history(period="1wk", interval="1h")[
                "Close"
            ].to_list(),
            "stock_month": ticker.history(period="1mo", interval="1d")[
                "Close"
            ].to_list(),
            "stock_year": ticker.history(period="1y", interval="1wk")[
                "Close"
            ].to_list(),
        }
    except:
        return {
            "stock_day": await get_stock_period(
                symbol, "TIME_SERIES_INTRADAY", 24, "60min"
            ),
            "stock_week": await get_stock_period(symbol, "TIME_SERIES_DAILY", 7),
            "stock_month": await get_stock_period(symbol, "TIME_SERIES_DAILY", 30),
            "stock_year": await get_stock_period(symbol, "TIME_SERIES_WEEKLY", 52),
        }


async def get_stock_period(symbol: str, period: str, num: int, interval="") -> list:
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
                keys = [key for key in data.keys() if "Time Series" in key]

                return (
                    [
                        float(entry["4. close"])
                        for entry in list(data[keys[0]].values())[:num]
                    ]
                    if len(keys) > 0
                    else []
                )
            else:
                return []


async def get_news(name: str) -> list[dict]:
    with open("news_whitelist.csv", "r") as f:
        whitelist = "".join([line.strip() for line in f.readlines()])
    print(whitelist)
    articles = []
    try:
        async with ClientSession(
            headers={"x-api-key": getenv("NEWSCATCHER_API_KEY")}
        ) as session:
            url = f'https://api.newscatcherapi.com/v2/search?q="{name}"&lang=en&sources={whitelist}&sort_by=date&page_size=50'
            async with session.get(url) as response:
                print("got response")
                if response.status == 200:
                    data = await response.json()
                    for article in data["articles"]:
                        articles.append(
                            {
                                "url": article["link"],
                                "headline": article["title"],
                                "publisher": article["clean_url"],
                                "date": article["published_date"],
                                "summary": article["excerpt"],
                            }
                        )
    except:
        num_articles = 50 - len(articles)
        async with ClientSession() as session:
            url = f'https://newsapi.org/v2/everything?q={name}&language=en&domains={whitelist}&pageSize={num_articles}&apiKey={getenv("NEWSAPI_API_KEY")}'
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    for article in data["articles"]:
                        articles.append(
                            {
                                "url": article["url"],
                                "headline": article["title"],
                                "publisher": article["source"]["name"],
                                "date": article["publishedAt"],
                                "summary": "",
                            }
                        )
    return articles


async def search_companies(query: str) -> list[str]:
    async with ClientSession() as session:
        async with session.get(
            f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
        ) as response:
            if response.status == 200:
                data = await response.json()
                # return the first 5 results
                return [
                    result["longname"] + ":" + result["symbol"]
                    for result in data["quotes"][:5]
                ]
            else:
                return []


def get_article_content(url: str) -> str:
    try:
        article = Article(url, language="en")
        article.download()
        article.parse()
        return article.text
    except:
        return ""
