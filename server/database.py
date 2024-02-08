from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
from flask-login import UserMixin
import werkzeug.security


# Create database
db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "User"

    # UserID: int
    id = db.Column(db.Integer, primary_key=True)

    # Email: string
    email = db.Column(db.String, unique=True)

    # Name: string
    name = db.Column(db.String)

    # Password(Hash): string
    password = db.Column(db.String)

    # OptEmail: boolean (has user opted into emails?)
    opt_email = db.Column(db.Boolean, default=False)

    def set_password(self, password: str) -> None:
        """Update this user's password."""
        self.password = werkzeug.security.generate_password_hash(password)

    def validate(self, password: str) -> bool:
        """Given a password, return if it is correct."""
        return werkzeug.security.check_password_hash(self.password, password)

    def get_notifications(self) -> list:  # list[Notification]:
        """Return list of notifications for this user."""
        pass

    def to_dict(self) -> dict:
        """Return object information to send to front-end."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "optEmail": self.opt_email
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
        return User(email=email,
                    name=name,
                    password=werkzeug.security.generate_password_hash(password),
                    opt_email=opt_email)

class Notification(db.Model):
    __tablename__ = "Notification"

    id = db.Column(db.Integer, primary_key=True)
    targetID = db.Column(db.Integer)
    TargetType = db.Column(db.Integer)
    message = db.Column(db.String)

class UserNotification(db.Model):
    __tablename__ = "UserNotification"

    UserID = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    NotificationID = db.Column(db.Integer, db.ForeignKey('Notification.id'), primary_key=True)

class Sector(db.Model):
    __tablename__ = "Sector"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

class UserSector(db.Model):
    __tablename__ = "UserSector"

    UserID = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    SectorID = db.Column(db.Integer, db.ForeignKey('Sector.id'), primary_key=True)

class Company(db.Model):
    __tablename__ = "Company"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    url = db.Column(db.String)
    description = db.Column(db.String)
    location = db.Column(db.String)
    sectorID = db.Column(db.Integer, db.ForeignKey('Sector.id'))
    marketCap = db.Column(db.Integer)
    ceo = db.Column(db.String)
    sentiment = db.Column(db.Decimal)
    lastScraped = db.Column(db.DateTime)

class Stock(db.Model):
    __tablename__ = "Stock"

    symbol = db.Column(db.String, primary_key=True)
    companyID = db.Column(db.Integer, db.ForeignKey('Company.id'))
    exchange = db.Column(db.String)
    marketCap = db.Column(db.Integer)
    stockPrice = db.Column(db.Decimal)
    stockChange = db.Column(db.Decimal)
    stockDay = db.Column(db.Array(db.Decimal))
    stockWeek = db.Column(db.Array(db.Decimal))
    stockMonth = db.Column(db.Array(db.Decimal))
    stockYear = db.Column(db.Array(db.Decimal))

class UserCompany(db.Model):
    __tablename__ = "UserCompany"

    UserID = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    CompanyID = db.Column(db.Integer, db.ForeignKey('Company.id'), primary_key=True)

class Article(db.Model):
    __tablename__ = "Article"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    headline = db.Column(db.String)
    publisher = db.Column(db.String)
    date = db.Column(db.DateTime)
    summary = db.Column(db.String)
    sentiment = db.Column(db.Decimal)

class Story(db.Model):
    __tablename__ = "Story"

    id = db.Column(db.Integer, primary_key=True)
    companyID = db.Column(db.Integer, db.ForeignKey('Company.id'))
    title = db.Column(db.String)
    sentiment = db.Column(db.Decimal)

class StoryArticle(db.Model):
    __tablename__ = "StoryArticle"

    StoryID = db.Column(db.Integer, db.ForeignKey('Story.id'), primary_key=True)
    ArticleID = db.Column(db.Integer, db.ForeignKey('Article.id'), primary_key=True)

class ArticleCompany(db.Model):
    __tablename__ = "ArticleCompany"

    ArticleID = db.Column(db.Integer, db.ForeignKey('Article.id'), primary_key=True)
    CompanyID = db.Column(db.Integer, db.ForeignKey('Company.id'), primary_key=True)

class StoryCompany(db.Model):
    __tablename__ = "StoryCompany"

    StoryID = db.Column(db.Integer, db.ForeignKey('Story.id'), primary_key=True)
    CompanyID = db.Column(db.Integer, db.ForeignKey('Company.id'), primary_key=True)