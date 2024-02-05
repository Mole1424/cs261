from flask_sqlalchemy import SQLAlchemy
# import werkzeug.security


# Create database
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "User"

    # UserID: int
    id = db.Column(db.Integer, primary_key=True)

    # Email: string
    email = db.Column(db.String)

    # Name: string
    name = db.Column(db.String)

    # Password(Hash): string
    password = db.Column(db.String)

    # OptEmail: boolean (has user opted into emails?)
    opt_email = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<db.User id={self.id}>"
