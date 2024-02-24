import data.database as db
from sqlalchemy import asc


def get_user_by_id(user_id: int) -> db.User | None:
    """Get a user by their ID."""
    return db.db.session.query(db.User).where(db.User.id == user_id).one_or_none()


def get_user_by_email(email: str) -> db.User | None:
    """Get user by their email."""
    return db.db.session.query(db.User).where(db.User.email == email).one_or_none()


def create_user(email: str, name: str, password: str, opt_email=False) -> db.User | None:
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


def get_company_details(company_id: int, user_id: int = None) -> tuple[db.Company, dict] | None:
    """Return (company, company_details)."""
    company = db.db.session.query(db.Company).where(db.Company.id == company_id).one_or_none()

    if not company:
        return None

    details = {
        **company.to_dict(),
        "sectors": list(map(lambda x: x.sector.to_dict(), db.CompanySector.get_by_company(company.id))),
        # TODO calculate stock delta (last day)
        "stockDelta": 0.0,
    }

    # If user was provided, check if they are following the company
    if user_id is not None:
        user_company = db.UserCompany.get(user_id, company.id)
        details['isFollowing'] = False if user_company is None else user_company.is_following()

    return company, details


def get_all_sectors() -> list[db.Sector]:
    """Get all sectors."""
    return db.db.session.query(db.Sector).order_by(asc(db.Sector.id)).all()
