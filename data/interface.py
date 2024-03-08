from asyncio import run
from datetime import datetime
from time import sleep
from typing import Callable, Optional

from flask import Flask
from sqlalchemy import and_, asc, desc

import data.api as api
import data.database as db
from analysis.analysis import sentiment_label, sentiment_score_to_text

FloatRange = tuple[float, float]


def string_to_list(
    string: str, convert_fn: Callable[[str], any], seperator: str = ","
) -> list:
    """Attempt to convert the input string to a list. String is in the form 'x<separator>y<separator>z...]. `convert_fn`
    is called on each element."""

    def func(x: str):
        try:
            return convert_fn(x.strip())
        except:
            return None

    return list(filter(lambda x: x is not None, map(func, string.split(seperator))))


def get_user_by_id(user_id: int) -> db.User | None:
    """Get a user by their ID."""
    return db.db.session.query(db.User).where(db.User.id == user_id).one_or_none()


def get_user_by_email(email: str) -> db.User | None:
    """Get user by their email."""
    return db.db.session.query(db.User).where(db.User.email == email).one_or_none()


def create_user(
    email: str, name: str, password: str, opt_email=False
) -> db.User | None:
    """Create a new user. If email exists will return None. Password will be hashed."""
    if get_user_by_email(email):
        return None
    user = db.User(
        email=email,
        name=name,
        password=password,
        opt_email=opt_email,
    )
    db.db.session.add(user)
    db.db.session.commit()
    return user


def is_valid_user(email: str, password: str) -> bool:
    """Check if the user is valid."""
    user = get_user_by_email(email)
    if user is None:
        return False
    return user.validate(password)


def get_company_details_by_id(
    company_id: int,
    user_id: int = None,
    load_stock=False,
    load_articles=False,
    article_count: int = 0,
) -> tuple[db.Company, dict] | None:
    """Return (company, company_details). Get full stock details?"""
    if (
        company := db.db.session.query(db.Company)
        .where(db.Company.id == company_id)
        .one_or_none()
    ):
        return company, get_company_details(
            company, user_id, load_stock, load_articles, article_count
        )
    else:
        return None


def get_company_details_by_symbol(
    symbol: str,
    user_id: int = None,
    load_stock=False,
    repeat=True,
    load_articles=False,
    article_count: int = 0,
) -> tuple[db.Company, dict] | None:
    """Return (company, company_details). Get full stock details?"""
    if (
        stock := db.db.session.query(db.Stock)
        .where(db.Stock.symbol == symbol)
        .one_or_none()
    ):
        company = db.db.session.query(db.Company).filter_by(id=stock.company_id).first()
        return company, get_company_details(
            company, user_id, load_stock, load_articles, article_count
        )
    elif repeat:
        add_company(symbol)
        return get_company_details_by_symbol(
            symbol, user_id, load_stock, False, load_articles, article_count
        )
    else:
        return None


def get_company_details(
    company: db.Company,
    user_id: int = None,
    load_stock=False,
    load_articles=False,
    article_count: int = 0,
) -> dict:
    """Get company details, given the company object."""

    details = {
        **company.to_dict(),
    }

    company_sectors = db.CompanySector.get_by_company(company.id)
    sectors = []
    for sector_db in company_sectors:
        sector = (
            db.db.session.query(db.Sector)
            .where(db.Sector.id == sector_db.sector_id)
            .one_or_none()
        )
        if sector:
            sectors.append(sector)
    details["sectors"] = [sector.to_dict() for sector in sectors]

    # Provide full stock data?
    stocks = db.Stock.get_all_by_company(company.id)
    if len(stocks) > 0:
        if load_stock:
            details["stock"] = stocks[0].to_dict()
        else:
            details["stockDelta"] = stocks[0].stock_change

    if load_stock:
        details["allStocks"] = [
            (stock.to_dict(), stock.stock_change) for stock in stocks
        ]

    # If user was provided, check if they are following the company
    if user_id is not None:
        user_company = db.UserCompany.get(user_id, company.id)
        details["isFollowing"] = (
            False if user_company is None else user_company.is_following()
        )
    # returns article_count most recent articles(default 4)
    if load_articles:
        articles = get_company_articles(company.id)
        if len(articles) > 0:
            if type(articles[0]) == db.Article:
                details["articles"] = list(
                    map(db.Article.to_dict, articles[:article_count])
                )
            else:
                details["articles"] = articles[:article_count]
        else:
            details["articles"] = []

    return details


def get_all_sectors() -> list[db.Sector]:
    """Get all sectors."""
    return db.db.session.query(db.Sector).order_by(asc(db.Sector.id)).all()


def get_followed_companies(user_id: int) -> list[tuple[db.Company, dict]] | None:
    """Return list of (company, company_details)"""
    followed_ids: list[int] = list(
        map(
            lambda uc: uc.company_id,
            filter(db.UserCompany.is_following, db.UserCompany.get_by_user(user_id)),
        )
    )
    return list(
        map(
            lambda company_id: get_company_details_by_id(company_id, user_id),
            followed_ids,
        )
    )


def search_companies(
    ceo: str = None,
    name: str = None,
    sectors: list[int] = None,
    sentiment: FloatRange = None,
    user_id: int = None,
    stock_price: FloatRange = None,
    market_cap: FloatRange = None,
) -> list[db.Company]:
    """Search companies given the following parameters."""

    query = db.db.session.query(db.Company)

    # Filter by CEO
    if ceo is not None:
        query = query.filter(db.Company.ceo.like("%" + ceo + "%"))

    # Filter by name
    if name is not None:
        query = query.filter(db.Company.name.like("%" + name + "%"))

    # Filter by sectors
    if sectors is not None and len(sectors) > 0:
        query = query.join(
            db.CompanySector, db.CompanySector.company_id == db.Company.id
        ).filter(db.CompanySector.sector_id.in_(sectors))

    # Include stock table?
    if stock_price is not None or market_cap is not None:
        query = query.join(db.Stock, db.Stock.company_id == db.Company.id)

    # Filter by market cap
    if market_cap is not None:
        query = query.filter(
            and_(
                db.Stock.market_cap >= market_cap[0],
                db.Stock.market_cap < market_cap[1],
            )
        )

    # Filter by stock price
    if stock_price is not None:
        query = query.filter(
            and_(
                db.Stock.stock_price >= stock_price[0],
                db.Stock.stock_price < stock_price[1],
            )
        )

    # Filter by sentiment score bounds
    if sentiment is not None:
        query = query.filter(
            and_(
                db.Company.sentiment >= sentiment[0],
                db.Company.sentiment < sentiment[1],
            )
        )
    result = query.all()

    if len(result) > 10 or name is None:
        return result
    # If less than 10 results from inside db, call api
    api_call_symbols = run(api.search_companies(name))
    for symbol in api_call_symbols:
        company = (
            db.db.session.query(db.Company.id)
            .filter(db.Company.name == symbol[0])
            .first()
        )
        if not company:
            result.append(add_company(symbol[1]))
        elif (
            not db.db.session.query(db.Stock)
            .filter(db.Stock.symbol == symbol[1])
            .first()
        ):
            add_stock(symbol[1], company[0])
    return result


def add_company(symbol: str, get_news=False) -> db.Company | None:
    # check if company exists
    db_symbol = (
        db.db.session.query(db.Stock).where(db.Stock.symbol == symbol).one_or_none()
    )
    if db_symbol:
        return (
            db.db.session.query(db.Company)
            .where(db.Company.id == db_symbol.company_id)
            .one_or_none()
        )

    info = run(api.get_company_info(symbol))
    company = db.Company(
        name=info["name"],
        url=info["url"],
        description=info["description"],
        location=info["location"],
        market_cap=info["market_cap"],
        ceo=info["ceo"],
        last_scraped=datetime.now(),
    )
    db.db.session.add(company)
    db.db.session.commit()

    sector_name = info["sector"]
    if not (
        sector := db.db.session.query(db.Sector)
        .where(db.Sector.name == sector_name)
        .one_or_none()
    ):
        sector = db.Sector(sector_name)
        db.db.session.add(sector)
        db.db.session.commit()

    db.db.session.add(db.CompanySector(company.id, sector.id))
    db.db.session.commit()

    add_stock(symbol, company.id)

    if get_news:
        get_company_articles(company.id)
        company.update_sentiment()
    return company


def add_stock(symbol: str, company_id: int) -> db.Stock | None:
    """Add a stock to a company."""
    if db.db.session.query(db.Stock).where(db.Stock.symbol == symbol).one_or_none():
        return None
    stock_info = run(api.get_stock_info(symbol))
    stock = db.Stock(
        symbol,
        company_id,
        stock_info["exchange"],
        stock_info["market_cap"],
        stock_info["stock_day"][-1] if stock_info["stock_day"] else 0,
        (
            stock_info["stock_day"][-1] - stock_info["stock_day"][0]
            if stock_info["stock_day"]
            else 0
        ),
        " ".join(map(str, stock_info["stock_day"])),
        " ".join(map(str, stock_info["stock_week"])),
        " ".join(map(str, stock_info["stock_month"])),
        " ".join(map(str, stock_info["stock_year"])),
    )
    db.db.session.add(stock)
    db.db.session.commit()
    return stock


def update_company_info(company_id: int) -> None:
    """Update company info."""
    company = (  # get company to update
        db.db.session.query(db.Company).where(db.Company.id == company_id).one_or_none()
    )

    if not company:
        return

    company_symbols = company.get_stocks()  # get all stocks for company
    combined_cap = 0  # combined market cap of all stocks
    new_symbols = run(api.get_symbols(company.name))

    for symbol in company_symbols:
        if symbol.symbol not in new_symbols:
            db.db.session.delete(symbol)
            db.db.session.commit()
            continue

        stock_info = run(api.get_stock_info(symbol.symbol))

        for key, value in stock_info.items():  # update stock info
            if value != "":
                if type(value) == list:
                    setattr(symbol, key, " ".join(map(str, value)))
                else:
                    setattr(symbol, key, value)

        symbol.stock_price = (
            stock_info["stock_day"][-1] if stock_info["stock_day"] else 0
        )
        symbol.stock_change = (
            stock_info["stock_day"][-1] - stock_info["stock_day"][0]
            if stock_info["stock_day"]
            else 0
        )
        db.db.session.commit()
        combined_cap += symbol.market_cap if symbol.market_cap else 0

    for symbol in new_symbols:
        if not (
            db.db.session.query(db.Stock).where(db.Stock.symbol == symbol).one_or_none()
        ):
            add_stock(symbol, company_id)

    company_info = run(api.get_company_info(company_symbols[0].symbol))
    for key, value in company_info.items():
        if value != "":
            setattr(company, key, value)
    company.last_scraped = datetime.now()
    company.market_cap = combined_cap
    db.db.session.commit()
    articles = get_company_articles(company_id)
    articles.sort(key=lambda x: abs(x.sentiment), reverse=True)
    if len(articles) > 0:
        if sentiment_score_to_text(abs(articles[0].sentiment)) == "Very Positive":
            add_article_notification(company, articles[0])
    old_sentiment = company.sentiment
    company.update_sentiment()
    if abs(old_sentiment - company.sentiment) > 0.25:
        diff_percent = abs(old_sentiment - company.sentiment) / old_sentiment * 100
        add_company_notification(company, diff_percent)


def add_article_notification(company: db.Company, article: db.Article) -> None:
    """Add article notification for company."""
    message = f"""There has been a recent news article about {company.name} that was {sentiment_score_to_text(article.sentiment).lower()}. 
    {article.headline} by {article.publisher}.
    You can read it at <a href="{article.url}">{article.url}</a>"""

    notification = db.Notification.create_article_notification(article.id, message)
    db.db.session.add(notification)
    db.db.session.commit()
    users = [
        get_user_by_id(user_company.user_id)
        for user_company in db.UserCompany.get_by_company(company.id)
    ]
    for user in users:
        db.db.session.add(db.UserNotification(user.id, notification.id))
    db.db.session.commit()


def add_company_notification(company: db.Company, sentiment_diff: float) -> None:
    message = f"""{company.name} has recieved an update.
    It's sentiment score has changed by {sentiment_diff}%.
    Find out more at <a href="localhost:5000/#company/{company.id}">localhost:5000/#company/{company.id}</a>"""

    notification = db.Notification.create_company_notification(company.id, message)
    db.db.session.add(notification)
    db.db.session.commit()
    users = [
        get_user_by_id(user_company.user_id)
        for user_company in db.UserCompany.get_by_company(company.id)
    ]
    for user in users:
        db.db.session.add(db.UserNotification(user.id, notification.id))
    db.db.session.commit()


def get_company_articles(company_id: int) -> list[db.Article] | None:
    company = (
        db.db.session.query(db.Company).where(db.Company.id == company_id).one_or_none()
    )  # get company to update
    if not company:
        return None

    if not (
        company.last_scraped is None or (datetime.now() - company.last_scraped).days > 1
    ):
        articles = company.get_articles()
        if len(articles) > 0:
            return articles

    news = run(api.get_news(company.name))  # get new news
    news_in_db = company.get_articles()
    articles: list[db.Article] = []
    for i in range(len(news)):
        if i >= len(news_in_db):
            # if new article add it
            article = db.Article(
                news[i]["url"],
                news[i]["headline"],
                news[i]["publisher"],
                news[i]["date"],
                news[i]["summary"],
            )
            db.db.session.add(article)
            db.db.session.commit()
            article.update_sentiment(sentiment_label(news[i]["full_text"])["score"])
            db.db.session.add(db.ArticleCompany(article.id, company_id))
            db.db.session.commit()
            articles.append(article)
        else:
            # add new info to existing article
            for key, value in news[i].items():
                if value != "":
                    setattr(news_in_db[i], key, value)
            articles.append(news_in_db[i])
    db.db.session.commit()
    return articles


def recent_articles(count: int = 10) -> Optional[list[dict]]:
    return list(
        map(
            db.Article.to_dict,
            db.db.session.query(db.Article)
            .order_by(desc(db.Article.date))
            .limit(count),
        )
    )


def article_by_id(article_id: int = None) -> db.Article | None:
    return db.Article.get_by_id(article_id)


# TODO
def delete_user(user: db.User) -> bool:
    try:
        db.db.session.query(db.UserNotification).filter(
            db.UserNotification.user_id == user.id
        ).delete()
        db.db.session.query(db.UserSector).filter(
            db.UserSector.user_id == user.id
        ).delete()
        db.db.session.query(db.UserCompany).filter(
            db.UserCompany.user_id == user.id
        ).delete()
        db.db.session.commit()
        return True
    except:
        return False


def update_loop(app: Flask) -> None:
    """Staggered throughout the day, update info on a company that's followed."""
    with app.app_context():
        while True:
            # get all companies in usercompany that are followed by a user
            companies = [
                db.db.session.query(db.Company)
                .filter(db.Company.id == company.company_id)
                .one_or_none()
                for company in db.db.session.query(db.UserCompany)
                .group_by(db.UserCompany.company_id)
                .all()
            ]
            for company in companies:
                update_company_info(company.id)
                # sleep for a day / number of companies
                for _ in range(86400 // max(len(companies), 1)):
                    sleep(1)
