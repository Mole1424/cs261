# NOTICE - Adding a new test
# When adding a new test, add the name of the test to the available_tests list
# AND add the test function to the if-else block at the bottom of the script
# AND IF APPROPRIATE add the test to default_script()

import argparse
import sys

# Import tests:
from testing.analysis.sentiment_test import run as run_sentiment_test

available_tests = ["sentiment"]

BUFFER = "\u001b[33;5m==============================\033[0m"  # Yellow
NBUFFER = BUFFER + "\n"

parser = argparse.ArgumentParser(
    description="Console interface for test suite. Running without options will run a default set of tests."
)
parser.add_argument(
    "-l",
    "--list",
    action="store_true",
    help="show list of all available tests and exit",
)
parser.add_argument(
    "-q", "--quiet", action="store_true", help="silences test announcements"
)
parser.add_argument(
    "-t",
    "--test",
    action="append",
    nargs="+",
    choices=available_tests,
    help="select specific tests to run",
)  # nargs='+' allows for 1 or more arguments
parser.add_argument(
    "-v", "--verbose", action="store_true", help="prints results of passed tests"
)

args = parser.parse_args()
argsdict = vars(args)


def default_script(verbose, narrate):
    print("Running Default Tests")
    print(NBUFFER)
    run_sentiment_test(show_pass=verbose, narrate=narrate)
    print(BUFFER)


if argsdict["list"]:
    print("Available tests:")
    for test in available_tests:
        print(test)
    sys.exit(0)

verbose = argsdict["verbose"]
narrate = not argsdict["quiet"]

# Execute tests that are requested
if argsdict["test"] is None:
    print("No tests pre-selected")
    default_script(verbose, narrate)
else:
    print(BUFFER)
    for test in argsdict["test"][0]:
        print("")
        if test == "sentiment":
            run_sentiment_test(show_pass=verbose, narrate=narrate)
        else:  # This should never be executed as the argparse should catch this
            print("Test not found: ", test)
        print(BUFFER)
