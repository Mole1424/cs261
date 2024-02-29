from asyncio import run
from typing import Callable

import data.api as api
import data.database as db
from sqlalchemy import asc, and_
from datetime import datetime
from time import sleep


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


def get_company_details(
    company_id: int, user_id: int = None, load_stock=False
) -> tuple[db.Company, dict] | None:
    """Return (company, company_details). Get full stock details?"""
    company = (
        db.db.session.query(db.Company).where(db.Company.id == company_id).one_or_none()
    )

    if not company:
        return None

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
    stock = db.Stock.get_by_company(company_id)
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

    return company, details


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
        map(lambda company_id: get_company_details(company_id, user_id), followed_ids)
    )


def search_companies(ceo: str="", name: str = "", sectors: list[int] = [], sentiment: list[float] = [], user_id: int = None, stockprice: list[float] = [], marketcap: list[int] = [], stockchange: bool = None) -> list[db.Company]:
    #get company ids that match ceo, name, sentiment
    #for returned ids, filter through sectors
    #for returned ids, filter through stocks
    
    sentimentFilter = and_(db.Company.sentiment >= sentiment[0], db.Company.sentiment <= sentiment[1]) if len(sentiment) == 2 else None
    sectorFilter = db.CompanySector.sector_id.in_(sectors) if len(sectors) > 0 else None
    #stockPriceFilter = and_(db.Stock.stock_price >= stockprice[0], db.Stock.stock_price <= stockprice[1]) if len(stockprice) == 2 else None
    #marketCapFilter = and_(db.Stock.marketcap >= marketcap[0], db.Stock.marketcap <= marketcap[1]) if len(marketcap) == 2 else None
    #stockChangeFilter = db.Stock.stock_change > 0 if stockchange else (db.Stock.stock_change < 0 if stockchange is not None else None)
    firstFilter = db.db.session.query(db.Company.id).filter(
                                                            db.Company.ceo.like('%' + ceo + '%'),
                                                            db.Company.name.like('%' + name + '%'),
                                                            sentimentFilter,
                                                            ).all()
    firstFilter = [int(result[0]) for result in firstFilter]

    secondFilter = db.db.session.query(db.CompanySector.company_id).filter( 
                                                                                and_(db.CompanySector.company_id.in_(firstFilter),
                                                                                sectorFilter)                                                                        
                                                                            )
    secondFilter = [int(result[0]) for result in secondFilter]
    
    #thirdFilter = db.db.session.query(db.Stock.company_id).filter(
    #                                                                stockChangeFilter,
    #                                                                marketCapFilter,
    #                                                                stockPriceFilter
    #                                                                )
    #thirdFilter = [int(result[0]) for result in thirdFilter]
    companies = [get_company_details(company_id, user_id)[1] for company_id in secondFilter]
    return companies






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

    news = run(api.get_news(company.name))
    news_in_db = company.get_articles()
    for i in range(len(news)):
        for key, value in news[i].items():
            if value != "":
                setattr(news[i], key, value)
    db.db.session.commit()


def update_loop() -> None:
    """Staggered throughout the day, update info on a company thats followed"""
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
            sleep(
                86400 / len(companies)
            )  # sleep for 24 hours divided by the number of companies
