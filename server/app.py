from datetime import datetime
from os import getenv, path, getcwd
from flask import Flask, render_template
import mimetypes

from server import constants
from data.database import *
from server.mail import mail
from server.routes import create_endpoints


def create_app() -> Flask:
    # Create Flask object
    app = Flask(
        constants.APP_NAME,
        static_url_path="/",
        static_folder="public/dist",
        template_folder="public/dist",
    )
    app.secret_key = getenv("FLASK_SECRET")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + path.join(
        path.abspath(getcwd()), constants.DATABASE_PATH
    )

    # Attach the database
    db.app = app
    db.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()
        dev = False
        if dev:
            add_data()

    # Attach the email service
    mail.app = app
    mail.init_app(app)

    # Setup file MIME types correctly -
    #  I noticed that Flask occasionally struggles with associating the correct mimetype
    #  This works as a fix
    mimetypes.init()
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("image/png", ".png")

    # Serve primary webpage
    @app.route("/", methods=["GET"])
    def index():
        return render_template(constants.APP_HTML_FILE, app_name=constants.APP_NAME)

    # Register remaining endpoints
    create_endpoints(app)

    return app


def add_data():
    db.drop_all()
    db.create_all()
    user = User(email="admin", name="admin", password="admin", opt_email=False)
    sector = Sector(name="Technology")
    apple = Company(
        name="Apple",
        url="https://www.apple.com",
        description="Apple Inc.",
        location="Cupertino, CA",
        market_cap=2000000000,
        ceo="Tim Cook",
        last_scraped=datetime.now(),
    )
    ibm = Company(
        "IBM",
        "https://www.ibm.com",
        "IBM Inc.",
        "Armonk, NY",
        1000000000,
        "Arvind Krishna",
        datetime.now(),
    )
    db.session.add(user)
    db.session.add(sector)
    db.session.add(apple)
    db.session.add(ibm)
    db.session.commit()
    apple_nasdaq = Stock("AAPL", apple.id, "NYQ", 1000, 150, 2, "", "", "", "")
    apple_ne = Stock("AAPL.NE", apple.id, "NEO", 1000, 150, 2, "", "", "", "")
    apple_ger = Stock("APC.DE", apple.id, "GER", 1000, 150, 2, "", "", "", "")
    ibm_nyq = Stock("IBM", ibm.id, "NYQ", 1000, 150, 2, "", "", "", "")
    ibm_ger = Stock("IBM.DE", ibm.id, "GER", 1000, 150, 2, "", "", "", "")
    db.session.add(apple_nasdaq)
    db.session.add(apple_ne)
    db.session.add(apple_ger)
    db.session.add(ibm_nyq)
    db.session.add(ibm_ger)
    db.session.commit()
    db.session.add(UserSector(user.id, sector.id))
    db.session.add(CompanySector(apple.id, sector.id))
    db.session.add(CompanySector(ibm.id, sector.id))
    db.session.add(UserCompany(user.id, apple.id, 1))
    db.session.commit()
