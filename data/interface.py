import api
import database as db
from sqlalchemy import asc


def get_user_by_id(self, user_id: int) -> db.User | None:
    """Get a user by their ID."""
    return db.db.session.query(db.User).where(db.User.id == user_id).one_or_none()


def get_user_by_email(self, email: str) -> db.User | None:
    """Get user by their email."""
    return db.db.session.query(db.User).where(db.User.email == email).one_or_none()


def create_user(
    self, email: str, name: str, password: str, opt_email=False
) -> db.User | None:
    """Create a new user. If email exists will return None. Password will be hashed."""
    if self.get_user_by_email(email):
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


def is_valid_user(self, email: str, password: str) -> bool:
    """Check if the user is valid."""
    user = self.get_user_by_email(email)
    if user is None:
        return False
    return user.validate(password)


def get_company_by_id(self, company_id: int) -> db.Company | None:
    """Get a company by their ID."""
    return (
        db.db.session.query(db.Company).where(db.Company.id == company_id).one_or_none()
    )


def get_all_sectors(self) -> list[db.Sector]:
    """Get all sectors."""
    return db.db.session.query(db.Sector).order_by(asc(db.Sector.id)).all()
