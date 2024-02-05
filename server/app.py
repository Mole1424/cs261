from os import getenv, path, getcwd
from flask import Flask
import mimetypes

from server import constants
from server.database import db
from server.mail import mail


def create_app() -> Flask:
    # Create Flask object
    app = Flask(constants.APP_NAME)
    app.secret_key = getenv('FLASK_SECRET')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + path.join(path.abspath(getcwd()), constants.DATABASE_PATH)

    # Attach the database
    db.app = app
    db.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Attach the email service
    mail.app = app
    mail.init_app(app)

    # Setup file MIME types correctly -
    #  I noticed that Flask occasionally struggles with associating the correct mimetype
    #  This works as a fix
    mimetypes.init()
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('text/css', '.css')
    mimetypes.add_type('image/png', '.png')

    @app.route("/", methods=['GET'])
    def index():
        return "<h1>Hello world!</h1>"

    return app
