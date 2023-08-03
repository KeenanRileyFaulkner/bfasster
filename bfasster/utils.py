import sys
import functools
import json


class TermColor:
    """Terminal codes for printing in color"""

    # pylint: disable=too-few-public-methods

    PURPLE = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_color(color, *msg):
    """Print mesage in color"""
    print(color + " ".join(str(item) for item in msg), TermColor.END)


def error(*msg, returncode=-1):
    """Print an error message and exit program"""

    print_color(TermColor.RED, "ERROR:", " ".join(str(item) for item in msg))
    sys.exit(returncode)


def only_once(func):
    """Decorator to ensure a function is only called once per program run
    (singleton method for non-singleton class)."""
    func._called = False

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not func._called:
            func._called = True
            return func(*args, **kwargs)

    return wrapper


def compare_json(old_file, new_json):
    """Takes an old json file a new json string and compares them to see if they are different"""
    if not (old_file).is_file():
        return False

    with open(old_file, "r") as f:
        old_json = json.load(f)
        return sort_json(old_json) == sort_json(json.loads(new_json))


def sort_json(item):
    """Sorts a json object recursively"""
    if isinstance(item, dict):
        return sorted((k, sort_json(v)) for k, v in item.items())
    if isinstance(item, list):
        return sorted(sort_json(x) for x in item)
    else:
        return item
