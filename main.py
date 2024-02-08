from sys import argv
from server import constants
from server.app import create_app
from dotenv import load_dotenv

if __name__ == "__main__":
    options = argv[1:]

    # Load .env file into environment
    load_dotenv()

    # Create and launch Flask application
    app = create_app()

    app.run(
        host=constants.FLASK_HOST,
        port=constants.FLASK_PORT,
        debug="--debug" in options
    )
