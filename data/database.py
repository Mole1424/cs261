from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
import werkzeug.security
from datetime import datetime
from sqlalchemy import asc
from analysis.analysis import sentiment_label

# Create database
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    name = db.Column(db.String)
    password = db.Column(db.String)
    opt_email = db.Column(db.Boolean, default=False)

    def __innit__(self, email: str, name: str, password: str, opt_email: bool = False):
        self.email = email
        self.name = name
        self.password = werkzeug.security.generate_password_hash(password)
        self.opt_email = opt_email

    def update_password(self, password: str) -> None:
        """Update this user's password."""
        self.password = werkzeug.security.generate_password_hash(password)
        db.session.commit()

    def update_user(self, name: str, email: str, opt_email: bool) -> None:
        """Update this user's information."""
        self.name = name
        self.email = email
        self.opt_email = opt_email
        db.session.commit()

    def validate(self, password: str) -> bool:
        """Given a password, return if it is correct."""
        return werkzeug.security.check_password_hash(self.password, password)

    def get_notifications(self) -> list[Notification]:
        """Return list of notifications for this user."""
        return (
            db.session.query(Notification)
            .join(UserNotification, Notification.id == UserNotification.notification_id)
            .where(UserNotification.user_id == self.id)
            .all()
        )

    def get_sectors(self) -> list[Sector]:
        """Return list of sectors this user is interested in."""
        return (
            db.session.query(Sector)
            .join(UserSector, Sector.id == UserSector.sector_id)
            .where(UserSector.user_id == self.id)
            .all()
        )

    def add_sector(self, sector_id: int) -> None:
        """Add a sector to user."""
        db.session.add(UserSector(user_id=self.id, sector_id=sector_id))
        db.session.commit()

    def remove_sector(self, sector_id: int) -> None:
        """Remove a sector from user."""
        db.session.query(UserSector).where(
            UserSector.user_id == self.id, UserSector.sector_id == sector_id
        ).delete()
        db.session.commit()

    def get_companies(self) -> list[Company]:
        """Return list of companies this user is interested in."""
        return (
            db.session.query(Company)
            .join(UserCompany, Company.id == UserCompany.company_id)
            .where(UserCompany.user_id == self.id)
            .all()
        )

    def add_company(self, company_id: int) -> None:
        """Add a company to user."""
        db.session.add(UserCompany(user_id=self.id, company_id=company_id))
        db.session.commit()

    def remove_company(self, company_id: int) -> None:
        """Remove a company from user."""
        db.session.query(UserCompany).where(
            UserCompany.user_id == self.id, UserCompany.company_id == company_id
        ).delete()
        db.session.commit()

    
    def add_sector(self, sector_id: int) -> Sector:
        """User follows sector, returns added row"""
        already_added = db.session.query(UserSector).where(UserSector.sector_id == sector_id, UserSector.user_id == self.id).first()
        if not already_added:
            sector_add = UserSector(user_id = self.id, sector_id = sector_id)
            db.session.add(sector_add)
            db.session.commit()
        return db.session.query(Sector).where(Sector.id == sector_id).first()

    def get_companies(self) -> list[Company]:
        """Return list of companies this user follows"""
        return db.session.query(Company).join(UserCompany, Company.id == UserCompany.company_id)\
            .where(UserCompany.user_id == self.id).all()

    def unfollow_company(self, company_id: int):
        """Remove a company from user follows."""
        db.session.query(UserCompany).where(UserCompany.user_id == self.id, UserCompany.company_id == company_id).delete()
        db.session.commit()
    
    def follow_company(self, company_id: int):
        """User follows a company"""
        already_added = db.session.query(UserCompany).where(UserCompany.company_id == company_id, UserCompany.user_id == self.id).first()
        if not already_added:
            company_add = UserCompany(user_id = self.id, company_id = company_id)
            db.session.add(company_add)
            db.session.commit()

    def to_dict(self) -> dict:
        """Return object information to send to front-end."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "optEmail": self.opt_email,
        }

    def __repr__(self) -> str:
        return f"<db.User id={self.id}>"


class Notification(db.Model):
    __tablename__ = "Notification"

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer)
    target_type = db.Column(db.Integer)
    message = db.Column(db.String)

    def __innit__(self, target_id: int, target_type: int, message: str):
        self.target_id = target_id
        self.target_type = target_type
        self.message = message

    def to_dict(self) -> dict:
        """Return object information to send to front-end."""
        return {
            "id": self.id,
            "targetId": self.target_id,
            "targetType": self.target_type,
            "message": self.message,
        }

    def get_users(self) -> list[User]:
        """Return list of users that have this notification."""
        return (
            db.session.query(User)
            .join(UserNotification, User.id == UserNotification.user_id)
            .where(UserNotification.notification_id == self.id)
            .all()
        )

    def add_users(self, user_ids: list[int]) -> None:
        """Add users to this notification."""
        for user_id in user_ids:
            db.session.add(UserNotification(user_id=user_id, notification_id=self.id))
        db.session.commit()


class UserNotification(db.Model):
    __tablename__ = "UserNotification"

    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), primary_key=True)
    notification_id = db.Column(
        db.Integer, db.ForeignKey("Notification.id"), primary_key=True
    )

    def __innit__(self, user_id: int, notification_id: int):
        self.user_id = user_id
        self.notification_id = notification_id


class Sector(db.Model):
    __tablename__ = "Sector"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __innit__(self, name: str):
        self.name = name

    def to_dict(self):
        return {"id": self.id, "name": self.name}

    def get_companies(self) -> list[Company]:
        """Return list of companies in this sector."""
        return db.session.query(Company).where(Company.sector_id == self.id).all()

    @staticmethod
    def get_all() -> list[Sector]:
        """Return list of sectors in the database."""
        return db.session.query(Sector).order_by(asc(Sector.id)).all()


class UserSector(db.Model):
    __tablename__ = "UserSector"

    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), primary_key=True)
    sector_id = db.Column(db.Integer, db.ForeignKey("Sector.id"), primary_key=True)

    def __innit__(self, user_id: int, sector_id: int):
        self.user_id = user_id
        self.sector_id = sector_id


class Company(db.Model):
    __tablename__ = "Company"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    url = db.Column(db.String)
    description = db.Column(db.String)
    location = db.Column(db.String)
    sector_id = db.Column(db.Integer, db.ForeignKey("Sector.id"))
    market_cap = db.Column(db.Integer)
    ceo = db.Column(db.String)
    sentiment = db.Column(db.Float, default=0.0)
    last_scraped = db.Column(db.DateTime)

    def __innit__(
        self,
        name: str,
        url: str,
        description: str,
        location: str,
        sector_id: int,
        market_cap: int,
        ceo: str,
        last_scraped: datetime.datetime,
    ):
        self.name = name
        self.url = url
        self.description = description
        self.location = location
        self.sector_id = sector_id
        self.market_cap = market_cap
        self.ceo = ceo
        self.last_scraped = last_scraped

    def update_company(
        self,
        name: str,
        url: str,
        description: str,
        location: str,
        sector_id: int,
        market_cap: int,
        ceo: str,
        last_scraped: datetime.datetime,
    ) -> None:
        """Update the company's information."""
        self.name = name
        self.url = url
        self.description = description
        self.location = location
        self.sector_id = sector_id
        self.market_cap = market_cap
        self.ceo = ceo
        self.last_scraped = last_scraped
        db.session.commit()

    def update_sentiment(self, sentiment: float) -> None:
        """Update the sentiment of this company."""
        self.sentiment = sentiment
        db.session.commit()

    def to_dict(self) -> dict:
        """Return object information to send to front-end."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "location": self.location,
            "sectorId": self.sector_id,
            "marketCap": self.market_cap,
            "ceo": self.ceo,
            "sentiment": self.sentiment,
            "lastScraped": self.last_scraped,
        }

    def __repr__(self) -> str:
        return f"<db.Company id={self.id}>"

    def get_stocks(self) -> list[Stock]:
        """Return list of stocks that have this company."""
        return db.session.query(Stock).where(Stock.company_id == self.id).all()

    def get_articles(self) -> list[Article]:
        """Return list of articles that have this company."""
        return (
            db.session.query(Article)
            .join(ArticleCompany, Article.id == ArticleCompany.article_id)
            .where(ArticleCompany.company_id == self.id)
            .all()
        )

    def get_stories(self) -> list[Story]:
        """Return list of stories that have this company."""
        return (
            db.session.query(Story)
            .join(StoryCompany, Story.id == StoryCompany.story_id)
            .where(StoryCompany.company_id == self.id)
            .all()
        )

    def get_sector(self) -> Sector:
        """Return the sector that this company is in."""
        return db.session.query(Sector).where(Sector.id == self.sector_id).first()

    def get_users(self) -> list[User]:
        """Return list of users that have this company."""
        return (
            db.session.query(User)
            .join(UserCompany, User.id == UserCompany.user_id)
            .where(UserCompany.company_id == self.id)
            .all()
        )

    def get_stocks(self) -> list[Stock]:
        """Return list of stocks that have this company."""
        return db.session.query(Stock).where(Stock.company_id == self.id).all()

    def to_dict(self):
        return{
            "id" : self.id,
            "name" : self.name,
            "url" : self.url,
            "description" : self.description,
            "location" : self.location,
            "sector_id" : self.sector_id,
            "market_cap" : self.market_cap,
            "ceo" : self.ceo,
            "sentiment" : self.sentiment,
            "last_scraped" : self.last_scraped
        }
     
    @staticmethod
    def get_details(company_id : int) -> Company:
        return db.session.query(Company).filter_by(id = company_id).first()


class Stock(db.Model):
    __tablename__ = "Stock"

    symbol = db.Column(db.String, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("Company.id"))
    exchange = db.Column(db.String)
    market_cap = db.Column(db.Integer)
    stock_price = db.Column(db.Float)
    stock_change = db.Column(db.Float)
    stock_day = db.Column(db.String)
    stock_week = db.Column(db.String)
    stock_month = db.Column(db.String)
    stock_year = db.Column(db.String)

    def __innit__(
        self,
        symbol: str,
        company_id: int,
        exchange: str,
        market_cap: int,
        stock_price: float,
        stock_change: float,
        stock_day: str,
        stock_week: str,
        stock_month: str,
        stock_year: str,
    ):
        self.symbol = symbol
        self.company_id = company_id
        self.exchange = exchange
        self.market_cap = market_cap
        self.stock_price = stock_price
        self.stock_change = stock_change
        self.stock_day = stock_day
        self.stock_week = stock_week
        self.stock_month = stock_month
        self.stock_year = stock_year

    def update_stock(
        self,
        market_cap: int,
        stock_price: float,
        stock_change: float,
        stock_day: str,
        stock_week: str,
        stock_month: str,
        stock_year: str,
    ) -> None:
        """Update the stock information."""
        self.market_cap = market_cap
        self.stock_price = stock_price
        self.stock_change = stock_change
        self.stock_day = stock_day
        self.stock_week = stock_week
        self.stock_month = stock_month
        self.stock_year = stock_year
        db.session.commit()


class UserCompany(db.Model):
    __tablename__ = "UserCompany"

    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("Company.id"), primary_key=True)
    # Temporary (probably)
    distance = db.Column(db.Float)

    def __innit__(self, user_id: int, company_id: int):
        self.user_id = user_id
        self.company_id = company_id


class Article(db.Model):
    __tablename__ = "Article"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    headline = db.Column(db.String)
    publisher = db.Column(db.String)
    date = db.Column(db.DateTime)
    summary = db.Column(db.String)
    sentiment = db.Column(db.Float, deafult=0.0)

    def __innit__(
        self,
        url: str,
        headline: str,
        publisher: str,
        date: datetime.datetime,
        summary: str,
    ):
        self.url = url
        self.headline = headline
        self.publisher = publisher
        self.date = date
        self.summary = summary

    def update_sentiment(self, sentiment: float) -> None:
        """Update the sentiment of this article."""
        self.sentiment = sentiment
        db.session.commit()

    def to_dict(self) -> dict:
        """Return object information to send to front-end."""
        return {
            "id": self.id,
            "url": self.url,
            "headline": self.headline,
            "publisher": self.publisher,
            "date": self.date,
            "summary": self.summary,
            "sentiment": self.sentiment,
        }

    def __repr__(self) -> str:
        return f"<db.Article id={self.id}>"

    def get_stories(self) -> list[Story]:
        """Return list of stories that have this article."""
        return (
            db.session.query(Story)
            .join(StoryArticle, Story.id == StoryArticle.story_id)
            .where(StoryArticle.article_id == self.id)
            .all()
        )

    def get_companies(self) -> list[Company]:
        """Return list of companies that have this article."""
        return (
            db.session.query(Company)
            .join(ArticleCompany, Company.id == ArticleCompany.company_id)
            .where(ArticleCompany.article_id == self.id)
            .all()
        )

    def set_score(self):
        """Set the sentiment score of the article"""
        # Should probably use entire text instead
        self.sentiment = sentiment_label(self.summary)['score']
        db.session.commit()


class Story(db.Model):
    __tablename__ = "Story"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("Company.id"))
    title = db.Column(db.String)
    sentiment = db.Column(db.Float, deafult=0.0)

    def __innit__(self, company_id: int, title: str):
        self.company_id = company_id
        self.title = title

    def update_sentiment(self, sentiment: float) -> None:
        """Update the sentiment of this story."""
        self.sentiment = sentiment
        db.session.commit()

    def to_dict(self) -> dict:
        """Return object information to send to front-end."""
        return {"id": self.id, "companyId": self.company_id, "title": self.title}

    def __repr__(self) -> str:
        return f"<db.Story id={self.id}>"

    def get_articles(self) -> list[Article]:
        """Return list of articles that have this story."""
        return (
            db.session.query(Article)
            .join(StoryArticle, Article.id == StoryArticle.article_id)
            .where(StoryArticle.story_id == self.id)
            .all()
        )

    def get_companies(self) -> list[Company]:
        """Return list of companies that have this story."""
        return (
            db.session.query(Company)
            .join(StoryCompany, Company.id == StoryCompany.company_id)
            .where(StoryCompany.story_id == self.id)
            .all()
        )


class StoryArticle(db.Model):
    __tablename__ = "StoryArticle"

    story_id = db.Column(db.Integer, db.ForeignKey("Story.id"), primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("Article.id"), primary_key=True)

    def __innit__(self, story_id: int, article_id: int):
        self.story_id = story_id
        self.article_id = article_id


class ArticleCompany(db.Model):
    __tablename__ = "ArticleCompany"

    article_id = db.Column(db.Integer, db.ForeignKey("Article.id"), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("Company.id"), primary_key=True)

    def __innit__(self, article_id: int, company_id: int):
        self.article_id = article_id
        self.company_id = company_id


class StoryCompany(db.Model):
    __tablename__ = "StoryCompany"

    stock_id = db.Column(db.Integer, db.ForeignKey("Story.id"), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("Company.id"), primary_key=True)

    def __innit__(self, story_id: int, company_id: int):
        self.story_id = story_id
        self.company_id = company_id
