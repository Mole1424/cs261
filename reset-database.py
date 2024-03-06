from os import getenv, getcwd, path
from dotenv import load_dotenv
import pandas as pd
from flask import Flask
from data.database import db, User, UserCompany
from data.interface import add_company, get_company_details_by_symbol
from server import constants


def reset_database():
    load_dotenv()

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


if __name__ == "__main__":
    app = Flask(constants.APP_NAME)
    app.secret_key = getenv("FLASK_SECRET")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + path.join(
        path.abspath(getcwd()), constants.DATABASE_PATH
    )

    # Attach the database
    db.app = app
    db.init_app(app)

    with app.app_context():
        db.create_all()
        dev = True
        if dev:
            reset_database()
