from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
import werkzeug.security
from datetime import datetime


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

    def update_name(self, new_name: str):
        """Update the user's name"""
        self.name = new_name
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

    def remove_sector(self, sector_id: int):
        """Remove a sector from user."""
        db.session.query(UserSector).where(
            UserSector.user_id == self.id, UserSector.sector_id == sector_id
        ).delete()
        db.session.commit()

    def add_sector(self, sector_id: int):
        """Add a sector to user."""
        db.session.add(UserSector(user_id=self.id, sector_id=sector_id))
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


class UserCompany(db.Model):
    __tablename__ = "UserCompany"

    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("Company.id"), primary_key=True)

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


class Story(db.Model):
    __tablename__ = "Story"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("Company.id"))
    title = db.Column(db.String)
    sentiment = db.Column(db.Float, deafult=0.0)

    def __innit__(self, company_id: int, title: str):
        self.company_id = company_id
        self.title = title


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
