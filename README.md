# cs261
A financial analysis platform, that aggregates news articles on a company and analyses their potential affect on a company's finances.

## Setup
This application requires `Python 3.12`, `pip` and `Node.js` to be installed.

- To download necessary Python libraries, run `pip install -r requirements.txt`.
- To download necessary Node libraries, run `npm install`.

### Environment Variables

The application requires a `.env` file to be present in the root directory.

The file should contain variables like those in exampleenv

## Building and Execution
To build the front-end code, please run `npm run build`.

*Development*: use `npm run build-watch` to watch files - webpack will re-build if a change is detected.

To start the server, run `python main.py`. Include the flag `--debug` to run in debug mode.
To stop the server, press `Ctrl+C`.

## Database

The database comes pre-loaded with the FTSE100 and S&P500 companies. Due to API limits, the database only contains 1 stock per company. These are then added to if you search the company on the website.

## Test Suite
To run the default selection of tests use `python test.py`.

To run specific test(s) use `python test.py -t test1 test2 etc`.

To see available tests use `-l`. To show the result of test passes include `-v`. To show help use `-h`.

## File Structure
The general structure of the project is given below. The descriptions of noteworthy folders and files are provided.

- `analysis/` - contains code for the machine learning aspects of the program.
  - `analysis.py` - contains the main analysis functions.
- `data/` - contains data for the application.
  - `api.py` - interacts with the APIs used in the application.
  - `database.db` - SQLite database file.
  - `database.py` - interacts with the database.
  - `interface.py` - provides an interface to the database and APIs.
  - `news_whitelist.csv` - A list of news sources that are considered reliable.
- `public/` - contains front-end source files.
  - `assets/` - contains images and other assets.
  - `dist/` - compiled output from webpack; served as static.
  - `src/` - JavaScript source files.
  - `styles/` - (S)CSS source files.
  - `index.html` - website template (note this is compiled into `dist/`).
- `server/` - contains back-end source files.
  - `app.py` - defines function `create_app` which creates the application.
  - `constants.py` - defines various non-sensitive constants to be used.
  - `routes.py` - defines the routes for the application.
- `testing/` - contains code and test data used to test various parts of the program.
- `util/` - contains utility files (not used directly by the application).
- `main.py` - application entry point.
- `test.py` - test suite entry point.
- `.env` - environment variables (this is not committed. Please ask team member's for latest version).
- `exampleenv` - example environment variables file.
- `reset-database.py` - script to reset the database to its initial state (pre populated with FTSE100 and S&F500 companies).

## APIs used

- [News API](https://newsapi.org/) - used to fetch news articles.
- [Newscatcher API](https://newscatcherapi.com/) - used to fetch news articles.
- [Alpha Vantage API](https://www.alphavantage.co/) - used to fetch stock data.
- [yfinance](https://pypi.org/project/yfinance/) - used to fetch stock data
