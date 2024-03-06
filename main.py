from sys import argv
from server import constants
from server.app import create_app
from dotenv import load_dotenv
from multiprocessing import Process
from data.interface import update_loop

if __name__ == "__main__":
    options = argv[1:]

    # Load .env file into environment
    load_dotenv()

    # Create and launch Flask application
    app = create_app()

    # Start the update loop DONT UNCOMMENT THIS AS ITS UNTESTED
    # p = Process(target=update_loop, args=(app,))
    # p.start()
    # p.join()

    app.run(
        host=constants.FLASK_HOST, port=constants.FLASK_PORT, debug="--debug" in options
    )
