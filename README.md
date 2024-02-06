# cs261
A financial analysis platform, that aggregates news articles on a company and analyses their potential affect on a companie's finances.

## Setup
This application requires `Python 3.12`, `pip` and `Node.js` to be installed.

- To download necessary Python libraries, run `pip install -r requirements.txt`.
- To download necessary Node libraries, run `npm install`.

## Building and Execution
To build the front-end code, please run `npm run build`.

*Development*: use `npm run build-watch` to watch files - webpack will re-build if a change is detected.

To start the server, run `python main.py`. Include the flag `--debug` to run in debug mode.
To stop the server, press `Ctrl+C`.

## File Structure
The general structure of the project is given below. The descriptions of noteworthy folders and files are provided.

- `data/` - contains data for the application.
  - `database.db` - SQLite database file.
- `public/` - contains front-end source files.
  - `dist/` - compiled output from webpack; served as static.
  - `src/` - JavaScript source files.
  - `styles/` - (S)CSS source files.
  - `index.html` - website template (note this is compiled into `dist/`).
- `server/` - contains back-end source files.
  - `app.py` - defines function `create_app` which creates the application.
  - `constants.py` - defines various non-sensitive constants to be used.
- `util/` - contains utility files (not used directly by the application).
- `main.py` - application entry point.
- `.env` - environment variables (this is not committed. Please ask team member's for latest version).
