import api
import database as db


class Interface:
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
