from os import getenv, getcwd, path

from dotenv import load_dotenv
import pandas as pd
from flask import Flask
import scipy.sparse as sp
from implicit.als import AlternatingLeastSquares
from joblib import dump

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
        add_company(symbol)
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


def init_train_hard():
    user_items = (
        db.session.query(UserCompany)
        .join(User, User.id == UserCompany.user_id)
        .filter(User.hard_ready >= 0, UserCompany.distance < 0)
    )

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
    dump(model, "data/rec_model.npz")


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
        reset_database()
        init_train_hard()
