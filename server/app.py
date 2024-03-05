from datetime import datetime
from os import getenv, path, getcwd
from flask import Flask, render_template
import mimetypes

from server import constants
from data.database import *
from data.interface import add_company, get_company_details_by_symbol
from server.mail import mail
from server.routes import create_endpoints
import pandas as pd

import scipy.sparse as sp
from implicit.als import AlternatingLeastSquares
from joblib import dump


def create_app() -> Flask:
    # Create Flask object
    app = Flask(
        constants.APP_NAME,
        static_url_path="/",
        static_folder="public/dist",
        template_folder="public/dist",
    )
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
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

        init_train_hard()

        dev = True
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

    admin_user = User("test@admin.com", "admin", getenv("ADMIN_PASSWORD"), False)
    db.session.add(admin_user)
    db.session.commit()

    print("added admin")

    # get s&p 500 data
    snp = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    symbols = [ticker.replace(".", "-") for ticker in snp[0]["Symbol"].tolist()]

    # get ftse 100 data
    ftse = pd.read_html("https://en.wikipedia.org/wiki/FTSE_100_Index")
    symbols += [ticker + ".L" for ticker in ftse[4]["Ticker"].to_list()]

    print("got symbols")

    for symbol in symbols:
        print("adding", symbol)
        add_company(symbol)

    print("following companies")

    initial_follow = ["AAPL", "GOOGL", "MSFT", "TSCO.L", "BP.L"]
    for symbol in initial_follow:
        db.session.add(
            UserCompany(admin_user.id, get_company_details_by_symbol(symbol)[0].id, -1)
        )
    db.session.commit()


def init_train_hard():
    user_items = db.session.query(UserCompany).join(User, User.id == UserCompany.user_id).filter(User.hard_ready >= 0, UserCompany.distance < 0)
    users = []
    items = []
    feedback = []
    for entry in user_items:
        users.append(entry.user_id)
        items.append(entry.company_id)
        if entry.distance == -1:
            feedback.append(1)
        else:
            feedback.append(-1)

    sparse_data = sp.csr_matrix((feedback, (users, items)))


    model = AlternatingLeastSquares(factors=10, regularization=0.1, iterations=50)
    model.fit(sparse_data)
    dump(model, 'data/rec_model.npz')


