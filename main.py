from server import constants
from server.app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(
        host=constants.FLASK_HOST,
        port=constants.FLASK_PORT,
        debug=constants.FLASK_DEBUG
    )
