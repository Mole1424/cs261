from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import werkzeug.security
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

    def get_notifications(self) -> list:  # list[Notification]:
        """Return list of notifications for this user."""
        pass

    def get_sectors(self) -> list[Sector]:
        """Return list of sectors this user is interested in."""
        return db.session.query(Sector).join(UserSector, Sector.id == UserSector.sector_id)\
            .where(UserSector.user_id == self.id).all()

    def remove_sector(self, sector_id: int):
        """Remove a sector from user."""
        db.session.query(UserSector).where(UserSector.user_id == self.id, UserSector.sector_id == sector_id).delete()
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

    @staticmethod
    def get_by_id(user_id: int) -> User:
        """Get a user by their ID."""
        return db.session.query(User).where(User.id == user_id).first()

    @staticmethod
    def get_by_email(email: str) -> User:
        """Get user by their email."""
        return db.session.query(User).where(User.email == email).first()

    @staticmethod
    def create(email: str, name: str, password: str, opt_email=False) -> User:
        """Create a new user. Assume email is unique. Password will be hashed."""
        return User(
            email=email,
            name=name,
            password=werkzeug.security.generate_password_hash(password),
            opt_email=opt_email,
        )


class Notification(db.Model):
    __tablename__ = "Notification"

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer)
    target_type = db.Column(db.Integer)
    message = db.Column(db.String)


class UserNotification(db.Model):
    __tablename__ = "UserNotification"

    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), primary_key=True)
    notification_id = db.Column(
        db.Integer, db.ForeignKey("Notification.id"), primary_key=True
    )


class Sector(db.Model):
    __tablename__ = "Sector"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

    @staticmethod
    def get_all() -> list[Sector]:
        """Return list of sectors in the database."""
        return db.session.query(Sector).order_by(asc(Sector.id)).all()


class UserSector(db.Model):
    __tablename__ = "UserSector"

    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), primary_key=True)
    sector_id = db.Column(db.Integer, db.ForeignKey("Sector.id"), primary_key=True)


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
    sentiment = db.Column(db.Float)
    last_scraped = db.Column(db.DateTime)

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


class UserCompany(db.Model):
    __tablename__ = "UserCompany"

    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("Company.id"), primary_key=True)
    # Temporary (probably)
    distance = db.Column(db.Float)


class Article(db.Model):
    __tablename__ = "Article"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    headline = db.Column(db.String)
    publisher = db.Column(db.String)
    date = db.Column(db.DateTime)
    summary = db.Column(db.String)
    sentiment = db.Column(db.Float)

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
    sentiment = db.Column(db.Float)


class StoryArticle(db.Model):
    __tablename__ = "StoryArticle"

    story_id = db.Column(db.Integer, db.ForeignKey("Story.id"), primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("Article.id"), primary_key=True)


class ArticleCompany(db.Model):
    __tablename__ = "ArticleCompany"

    article_id = db.Column(db.Integer, db.ForeignKey("Article.id"), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("Company.id"), primary_key=True)


class StoryCompany(db.Model):
    __tablename__ = "StoryCompany"

    stock_id = db.Column(db.Integer, db.ForeignKey("Story.id"), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("Company.id"), primary_key=True)
