from os import getenv, getcwd, path

from dotenv import load_dotenv
import pandas as pd
from flask import Flask
from time import sleep

from data.database import db, User, UserCompany
from data.interface import add_company, get_company_details_by_symbol
from server import constants
from datetime import datetime


def reset_database():
    load_dotenv()

    db.drop_all()
    db.create_all()

    admin_user = User("test@admin.com", "admin", getenv("ADMIN_PASSWORD"), False)
    db.session.add(admin_user)
    db.session.commit()

    other_user = User("otheruser@gmail.com", "other", getenv("ADMIN_PASSWORD"), False)
    db.session.add(other_user)
    db.session.commit()

    print("added users")

    symbols = []

    # get s&p 500 data
    snp = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    symbols += [ticker.replace(".", "-") for ticker in snp[0]["Symbol"].tolist()]

    # get ftse 100 data
    ftse = pd.read_html("https://en.wikipedia.org/wiki/FTSE_100_Index")
    symbols += [ticker + ".L" for ticker in ftse[4]["Ticker"].to_list()]

    print("got symbols")

    for symbol in symbols:
        print("adding", symbol)
        add_company(symbol, True)
        sleep(1)
        print("% done", symbols.index(symbol) / len(symbols) * 100)

    print("following companies")

    admin_follow = ["AAPL", "GOOGL", "MSFT", "TSCO.L", "BP.L"]
    test_follow = ["PFE", "AZN.L", "BNTX", "SVA", "MRNA"]
    for symbol in admin_follow:
        company = get_company_details_by_symbol(symbol)[0].id
        admin_user.add_company(company)
    for symbol in test_follow:
        company = get_company_details_by_symbol(symbol)[0].id
        other_user.add_company(company)
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
        start_time = datetime.now()
        reset_database()
    print("Time taken:", datetime.now() - start_time)
