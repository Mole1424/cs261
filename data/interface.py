from asyncio import run
from typing import Callable

import data.api as api
import data.database as db
from sqlalchemy import asc, and_, desc
from datetime import datetime
from time import sleep
from flask import Flask


FloatRange = tuple[float, float]


def string_to_list(string: str, convert_fn: Callable[[str], any]) -> list:
    """Attempt to convert the input string to a list. String is in the form [x, y, z, ...]. `convert_fn`
    is called on each element."""

    def func(x: str):
        try:
            return convert_fn(x.strip())
        except:
            return None

    return list(filter(lambda x: x is not None, map(func, string[1:-1].split(","))))


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
    company_id: int, user_id: int = None, load_stock=False
) -> tuple[db.Company, dict] | None:
    """Return (company, company_details). Get full stock details?"""
    if (
        company := db.db.session.query(db.Company)
        .where(db.Company.id == company_id)
        .one_or_none()
    ):
        return company, get_company_details(company, user_id, load_stock)
    else:
        return None


def get_company_details_by_symbol(
    symbol: str, user_id: int = None, load_stock=False
) -> tuple[db.Company, dict] | None:
    """Return (company, company_details). Get full stock details?"""
    if (
        stock := db.db.session.query(db.Stock)
        .where(db.Stock.symbol == symbol)
        .one_or_none()
    ):
        company = db.db.session.query(db.Company).filter_by(id=stock.company_id).first()
        return company, get_company_details(company, user_id, load_stock)
    else:
        return None


def get_company_details(
    company: db.Company, user_id: int = None, load_stock=False
) -> dict:
    """Get company details, given the company object."""
    details = {
        **company.to_dict(),
        "sectors": list(
            map(
                lambda x: x.sector.to_dict(),
                db.CompanySector.get_by_company(company.id),
            )
        ),
    }

    # Provide full stock data?
    stock = db.Stock.get_by_company(company.id)
    if stock is not None:
        if load_stock:
            details["stock"] = stock.to_dict()
        else:
            details["stockDelta"] = stock.stock_change

    # If user was provided, check if they are following the company
    if user_id is not None:
        user_company = db.UserCompany.get(user_id, company.id)
        details["isFollowing"] = (
            False if user_company is None else user_company.is_following()
        )

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

    return query.all()


def add_company(symbol: str) -> db.Company | None:
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
    return company


def add_stock(symbol: str, company_id: int) -> db.Stock | None:
    """Add a stock to a company."""
    stock_info = run(api.get_stock_info(symbol))
    stock = db.Stock(
        symbol,
        company_id,
        stock_info["exchange"],
        stock_info["market_cap"],
        stock_info["stock_day"][-1],
        stock_info["stock_day"][-1] - stock_info["stock_day"][0],
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

    company_symbols = (  # get all stocks for the company
        db.db.session.query(db.Stock).where(db.Stock.company_id == company_id).all()
    )
    combined_cap = 0  # combined market cap of all stocks

    for symbol in company_symbols:
        stock_info = run(api.get_stock_info(symbol.symbol))

        for key, value in stock_info.items():  # update stock info
            if value != "":
                if type(value) == list:
                    setattr(symbol, key, " ".join(map(str, value)))
                else:
                    setattr(symbol, key, value)

        symbol.stock_price = stock_info["stock_day"][-1]
        symbol.stock_change = stock_info["stock_day"][-1] - stock_info["stock_day"][0]
        db.db.session.commit()
        combined_cap += symbol.market_cap

    company_info = run(api.get_company_info(company_symbols[0].symbol))
    for key, value in company_info.items():
        if value != "":
            setattr(company, key, value)
    company.last_scraped = datetime.now()
    company.market_cap = combined_cap
    db.db.session.commit()
    get_company_articles(company_id)


def get_company_articles(company_id: int) -> list[db.Article] | None:
    company = (
        db.db.session.query(db.Company).where(db.Company.id == company_id).one_or_none()
    )  # get company to update
    if not company:
        return None

    news = run(api.get_news(company.name))  # get new newa
    news_in_db = company.get_articles()
    for i in range(50):
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
            db.db.session.add(db.ArticleCompany(article.id, company_id))
            db.db.session.commit()
        else:
            # add new info to existing article
            for key, value in news[i].items():
                if value != "":
                    setattr(news_in_db[i], key, value)
    db.db.session.commit()

def recent_articles(count: int = 10) -> list[db.Article] | None:
    return db.db.session.query(db.Article).order_by(desc(db.Article.date)).limit(count)

def article_By_ID(articleID: int = None) -> db.Article | None:
    return db.Article.get_by_id(articleID)

def update_loop(app: Flask) -> None:
    """Staggered throughout the day, update info on a company thats followed"""
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
                sleep(86400 / max(len(companies), 1))
