from os import getenv, path, getcwd
from flask import Flask, render_template
import mimetypes

from data.database import db
from server import constants
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
