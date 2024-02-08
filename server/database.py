from __future__ import annotations
from flask_sqlalchemy import SQLAlchemy
import werkzeug.security


# Create database
db = SQLAlchemy()


class User(db.Model):
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
