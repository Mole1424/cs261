from sys import argv
from threading import Thread

from dotenv import load_dotenv

from data.interface import update_loop
from server import constants
from server.app import create_app

if __name__ == "__main__":
    options = argv[1:]

    # Load .env file into environment
    load_dotenv()

    # Create and launch Flask application
    app = create_app()

    # Start the update loop DONT UNCOMMENT THIS AS ITS UNTESTED
    # update_thread = Thread(target=update_loop, args=(app,))
    # update_thread.daemon = True
    # update_thread.start()

    app.run(
        host=constants.FLASK_HOST,
        port=constants.FLASK_PORT,
        debug="--debug" in options,
    )
